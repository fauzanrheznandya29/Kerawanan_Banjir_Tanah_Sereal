import streamlit as st
import folium
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rio_mask
import numpy as np
from folium.plugins import MousePosition, MiniMap, Fullscreen, MeasureControl
from matplotlib import colors
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium
from branca.element import MacroElement
from jinja2 import Template

from utils.ui import load_css, page_header, section_title, footer

load_css()


# =====================================================
# Kontrol kompas (Leaflet Control asli, menyatu di dalam
# container peta agar tetap tampil saat mode fullscreen)
# =====================================================


class CompassControl(MacroElement):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        var compass_{{ this.get_name() }} = L.control({position: '{{ this.position }}'});
        compass_{{ this.get_name() }}.onAdd = function(map) {
            var div = L.DomUtil.create('div', 'wg-compass');
            div.innerHTML = `
                <svg width="54" height="54" viewBox="0 0 54 54" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="27" cy="27" r="25" fill="rgba(18,26,43,0.88)" stroke="#ffffff" stroke-width="1.5"/>
                    <polygon points="27,7 32,27 27,23 22,27" fill="#e53935"/>
                    <polygon points="27,47 22,27 27,31 32,27" fill="#e6edf3"/>
                    <text x="27" y="16" text-anchor="middle" fill="#ffffff"
                          font-size="10" font-family="Arial, sans-serif" font-weight="bold">N</text>
                </svg>
            `;
            L.DomEvent.disableClickPropagation(div);
            return div;
        };
        compass_{{ this.get_name() }}.addTo({{ this._parent.get_name() }});
        {% endmacro %}
        """
    )

    def __init__(self, position="topright"):
        super().__init__()
        self._name = "CompassControl"
        self.position = position


# =====================================================
# Header
# =====================================================

page_header(
    eyebrow="Peta Interaktif",
    title="🗺️ Peta Kerawanan Banjir",
    description=(
        "Kecamatan Tanah Sareal, Kota Bogor — hasil klasifikasi indeks kerawanan banjir "
        "dari analisis Weighted Overlay. Gunakan panel kontrol di sidebar untuk mengatur "
        "basemap, layer, dan transparansi."
    ),
    badges=["📡 5 Kelas Kerawanan", "🧭 Alat Ukur", "🛰️ Multi-Basemap"],
)

# =====================================================
# Load data (cached agar tetap responsif saat kontrol diubah)
# =====================================================


@st.cache_data(show_spinner=False)
def load_vector():
    boundary = gpd.read_file("data/boundary/boundary_tanah_sareal.geojson")
    kelurahan = gpd.read_file("data/boundary/kelurahan_tanah_sareal.geojson")
    river = gpd.read_file("data/river/sungai_tanah_sareal_clip.geojson")
    river = river[river.geometry.type.isin(["LineString", "MultiLineString"])]
    return boundary, kelurahan, river


RASTER_CMAP = colors.ListedColormap(
    ["#1a9850", "#7cb342", "#f9a825", "#ef6c00", "#d32f2f"]
)

# Raster parameter tambahan (selain Indeks Kerawanan Banjir), nama ditulis
# dalam Bahasa Indonesia agar konsisten dengan istilah yang dipakai di
# halaman Tentang. Menggunakan skema warna yang sama (RASTER_CMAP) agar
# konsisten secara visual dengan raster kerawanan banjir.
PARAM_RASTERS = [
    ("data/raster/dem_class.tif", "🏔 Elevasi (DEM)"),
    ("data/raster/slope_class_resampled.tif", "⛰ Kemiringan Lereng"),
    ("data/raster/rainfall_class.tif", "🌧 Curah Hujan"),
    ("data/raster/river_class.tif", "🌊 Jarak ke Sungai"),
    ("data/raster/landcover_class_resampled.tif", "🌿 Tutupan Lahan"),
]


@st.cache_data(show_spinner=False)
def load_raster_rgba(path):
    """Baca raster apa pun, clip ke batas kecamatan (agar bentuknya mengikuti
    wilayah kajian seperti raster yang sudah ter-clip), normalisasi dinamis
    (min-max), lalu warnai dengan skema warna yang sama dengan raster
    kerawanan banjir agar konsisten."""
    boundary_gdf = gpd.read_file("data/boundary/boundary_tanah_sareal.geojson")

    with rasterio.open(path) as raster:
        boundary_r = boundary_gdf.to_crs(raster.crs) if raster.crs else boundary_gdf
        geoms = [geom.__geo_interface__ for geom in boundary_r.geometry]

        try:
            # filled=False -> hasilnya masked array, jadi tidak perlu memaksa
            # nilai sentinel ke dtype asli raster (aman untuk uint8, int16, dll).
            clipped, transform = rio_mask(raster, geoms, crop=True, filled=False)
            data = clipped[0]
            image = data.data.astype(float)
            image[np.ma.getmaskarray(data)] = np.nan
            if raster.nodata is not None:
                image = np.where(image == raster.nodata, np.nan, image)
            height, width = image.shape
            left, bottom, right, top = rasterio.transform.array_bounds(height, width, transform)
        except ValueError:
            # Geometri tidak beririsan dengan raster; fallback ke raster utuh.
            image = raster.read(1).astype(float)
            if raster.nodata is not None:
                image = np.where(image == raster.nodata, np.nan, image)
            left, bottom, right, top = raster.bounds.left, raster.bounds.bottom, raster.bounds.right, raster.bounds.top

        bounds = [[bottom, left], [top, right]]

    valid = image[~np.isnan(image)]
    if valid.size == 0:
        return None, bounds

    vmin, vmax = np.nanmin(image), np.nanmax(image)
    if vmax > vmin:
        norm = (image - vmin) / (vmax - vmin)
    else:
        norm = np.zeros_like(image)

    rgba = (RASTER_CMAP(norm) * 255).astype(np.uint8)
    rgba[..., 3] = np.where(np.isnan(image), 0, 255)
    return rgba, bounds


boundary, kelurahan, river = load_vector()

rgba, raster_bounds = load_raster_rgba(
    "data/raster/Flood_Index.tif"
)

# =====================================================
# Panel kontrol (sidebar) — gaya WebGIS profesional
# =====================================================

st.sidebar.markdown("### 🎛️ Panel Kontrol Peta")

basemap_choice = st.sidebar.selectbox(
    "🛰️ Basemap",
    ["CartoDB Positron (Terang)", "CartoDB Dark Matter (Gelap)", "Esri Satellite", "OpenStreetMap"],
    index=0,
)

st.sidebar.markdown("**📚 Layer Tampil**")
show_raster = st.sidebar.checkbox("🌊 Indeks Kerawanan Banjir", value=True)
show_boundary = st.sidebar.checkbox("🟦 Batas Kecamatan", value=True)
show_kelurahan = st.sidebar.checkbox("⬛ Batas Kelurahan", value=True)
show_river = st.sidebar.checkbox("💧 Jaringan Sungai", value=True)

st.sidebar.markdown("**🧬 Layer Parameter (Raster)**")
show_param = {}
for path, label in PARAM_RASTERS:
    show_param[path] = st.sidebar.checkbox(label, value=False, key=f"param_{path}")

opacity = st.sidebar.slider("🎚️ Transparansi Raster", 0.0, 1.0, 0.85, 0.05)

with st.sidebar.expander("ℹ️ Legenda Kelas Kerawanan", expanded=False):
    legend_items = [
        ("#1a9850", "Sangat Rendah"),
        ("#7cb342", "Rendah"),
        ("#f9a825", "Sedang"),
        ("#ef6c00", "Tinggi"),
        ("#d32f2f", "Sangat Tinggi"),
    ]
    for color_hex, label in legend_items:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin:3px 0;">'
            f'<span style="width:16px;height:16px;border-radius:4px;background:{color_hex};display:inline-block;"></span>'
            f'<span style="font-size:13px;">{label}</span></div>',
            unsafe_allow_html=True,
        )

# =====================================================
# Bangun peta
# =====================================================

basemap_tiles = {
    "CartoDB Positron (Terang)": "CartoDB Positron",
    "CartoDB Dark Matter (Gelap)": "CartoDB Dark_Matter",
    "OpenStreetMap": "OpenStreetMap",
}

center = boundary.geometry.union_all().centroid

if basemap_choice == "Esri Satellite":
    m = folium.Map(location=[center.y, center.x], zoom_start=14, tiles=None, control_scale=True)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="🛰 Esri Satellite",
        overlay=False,
        control=True,
    ).add_to(m)
else:
    m = folium.Map(
        location=[center.y, center.x],
        zoom_start=14,
        tiles=basemap_tiles[basemap_choice],
        control_scale=True,
    )

# Tambahkan opsi basemap lain agar tetap bisa dipilih dari layer control
for label, tile in basemap_tiles.items():
    if label != basemap_choice:
        folium.TileLayer(tiles=tile, name=f"🗺️ {label}", overlay=False, control=True, show=False).add_to(m)
if basemap_choice != "Esri Satellite":
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="🛰 Esri Satellite",
        overlay=False,
        control=True,
        show=False,
    ).add_to(m)

# Plugin GIS profesional
Fullscreen(position="topright").add_to(m)
MousePosition(position="bottomright", separator=" | ", prefix="Koordinat:").add_to(m)
MiniMap(toggle_display=True, position="bottomleft").add_to(m)
MeasureControl(position="topright", primary_length_unit="meters", primary_area_unit="hectares").add_to(m)
CompassControl(position="topright").add_to(m)

# Layer sesuai pilihan sidebar
if show_raster and rgba is not None:
    ImageOverlay(
        image=rgba,
        bounds=raster_bounds,
        opacity=opacity,
        name="🌊 Indeks Kerawanan Banjir"
    ).add_to(m)

for path, label in PARAM_RASTERS:
    if show_param.get(path):
        param_rgba, param_bounds = load_raster_rgba(path)
        if param_rgba is not None:
            ImageOverlay(image=param_rgba, bounds=param_bounds, opacity=opacity, name=label).add_to(m)

if show_boundary:
    folium.GeoJson(
        boundary,
        name="🟦 Batas Kecamatan",
        style_function=lambda x: {"color": "#1a1a1a", "weight": 3, "opacity": 1, "fillOpacity": 0},
    ).add_to(m)

if show_kelurahan:
    folium.GeoJson(
        kelurahan,
        name="⬛ Batas Kelurahan",
        style_function=lambda x: {"color": "#6d4c2f", "weight": 3, "opacity": 0.9, "fillOpacity": 0},
        highlight_function=lambda x: {
            "color": "#ffd54f",
            "weight": 4,
            "opacity": 1,
            "fillOpacity": 0.20,
            "fillColor": "#ffd54f",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name"],
            aliases=["Desa/Kelurahan:"],
            localize=True,
            sticky=True,
            labels=True,
            style="""
                background-color:#ffffff;
                color:#111827;
                font-size:14px;
                font-family:'Inter',Arial,sans-serif;
                font-weight:600;
                padding:8px 14px;
                border-radius:8px;
                box-shadow:0 6px 18px rgba(0,0,0,.28);
                border:1px solid rgba(0,0,0,.08);
            """,
        ),
    ).add_to(m)

if show_river:
    folium.GeoJson(
        river,
        name="💧 Jaringan Sungai",
        style_function=lambda x: {"color": "#4fc3f7", "weight": 2.5, "opacity": 0.9},
    ).add_to(m)

# Catatan: kontrol layer & legenda kelas kerawanan sudah tersedia di panel
# sidebar ("Panel Kontrol Peta"), sehingga tidak lagi ditumpuk di atas peta
# agar tampilan visualisasi lebih bersih.

# Zoom otomatis ke boundary
xmin, ymin, xmax, ymax = boundary.total_bounds
padding = 0.001
m.fit_bounds([[ymin - padding, xmin - padding], [ymax + padding, xmax + padding]])

# =====================================================
# Render peta dalam frame kartu
# =====================================================

with st.container(border=True):
    st_folium(m, width=None, height=740, returned_objects=[])

# =====================================================
# Info bar bawah peta
# =====================================================

st.write("")
i1, i2, i3, i4 = st.columns(4)
i1.metric("Luas Wilayah", f"{boundary.to_crs(32748).area.sum() / 10000:,.1f} Ha")
i2.metric("Jumlah Kelurahan", f"{len(kelurahan)}")
i3.metric("Panjang Ruas Sungai", f"{river.to_crs(32748).length.sum() / 1000:,.1f} km")
i4.metric("Sistem Klasifikasi", "5 Kelas")

st.caption(
    "💡 Gunakan ikon layer di pojok kanan atas peta untuk mengganti basemap, "
    "ikon penggaris untuk mengukur jarak/luas, dan panel kontrol di sidebar "
    "untuk menampilkan/menyembunyikan layer."
)

footer(
    "WebGIS Analisis Kerawanan Banjir &middot; Kecamatan Tanah Sareal, Kota Bogor<br>"
    "Sumber basemap: CartoDB &amp; Esri &middot; Data diolah menggunakan metode Weighted Overlay"
)
