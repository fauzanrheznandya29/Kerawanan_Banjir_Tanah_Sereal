import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import plotly.express as px
from utils.ui import load_css, page_header, section_title, footer

load_css()

# ==========================================================
# MEMBACA DATA
# ==========================================================

df = pd.read_csv("data/statistik/Statistik_Kerawanan_Banjir.csv")

total_luas = df["Luas (ha)"].sum()
total_pixel = df["Pixel"].sum()
jumlah_kelas = len(df)
kelas_dominan = df.loc[df["Persentase (%)"].idxmax(), "Kelas"]
persentase_dominan = df["Persentase (%)"].max()

warna = {
    "Sangat Rendah": "#1a9850",
    "Rendah": "#7cb342",
    "Sedang": "#f9a825",
    "Tinggi": "#ef6c00",
    "Sangat Tinggi": "#d32f2f",
}

KELAS_URUTAN = ["Sangat Tinggi", "Tinggi", "Sedang", "Rendah", "Sangat Rendah"]
KELAS_LABEL = {1: "Sangat Rendah", 2: "Rendah", 3: "Sedang", 4: "Tinggi", 5: "Sangat Tinggi"}


@st.cache_data(show_spinner=False)
def hitung_statistik_per_kelurahan():
    """Zonal statistics: hitung persentase tiap kelas kerawanan untuk setiap desa/kelurahan."""
    kelurahan = gpd.read_file("data/boundary/kelurahan_tanah_sareal.geojson")

    with rasterio.open("data/raster/Flood_Class.tif") as src:
        kelurahan_r = kelurahan.to_crs(src.crs)
        rows = []
        for _, feat in kelurahan_r.iterrows():
            nama = feat.get("name", "Tidak diketahui")
            try:
                out_image, _ = mask(src, [feat.geometry.__geo_interface__], crop=True, nodata=src.nodata)
            except ValueError:
                continue
            arr = out_image[0]
            valid = arr[arr != src.nodata] if src.nodata is not None else arr[~np.isnan(arr)]
            valid = valid[~np.isnan(valid)]
            total = valid.size
            if total == 0:
                continue
            for kelas_val, label in KELAS_LABEL.items():
                pct = float((valid == kelas_val).sum()) / total * 100
                rows.append({"Kelurahan": nama, "Kelas": label, "Persentase (%)": pct})

    return pd.DataFrame(rows)


# ==========================================================
# HEADER
# ==========================================================

page_header(
    eyebrow="Statistik Hasil Analisis",
    title="📊 Statistik Kerawanan Banjir",
    description=(
        "Distribusi luas dan persentase tiap kelas kerawanan banjir di Kecamatan Tanah Sareal, "
        "dihasilkan dari analisis <b>Weighted Overlay</b> terhadap lima parameter spasial."
    ),
    badges=[f"📐 {total_luas:,.0f} Ha", f"🏷️ {jumlah_kelas} Kelas", f"🥇 Dominan: {kelas_dominan}"],
)

# ==========================================================
# RINGKASAN STATISTIK
# ==========================================================

section_title("📌 Ringkasan Statistik")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Luas Wilayah", f"{total_luas:.2f} Ha")
col2.metric("Jumlah Kelas", jumlah_kelas)
col3.metric("Kelas Dominan", kelas_dominan)
col4.metric("Persentase Dominan", f"{persentase_dominan:.2f}%")
col5.metric("Total Pixel", f"{total_pixel:,}")

st.markdown("---")

# ==========================================================
# GRAFIK BATANG
# ==========================================================

section_title("📊 Distribusi Tingkat Kerawanan")

fig_bar = px.bar(
    df, x="Kelas", y="Persentase (%)", color="Kelas",
    color_discrete_map=warna, text="Persentase (%)",
)
fig_bar.update_layout(
    template="plotly_dark", height=480, showlegend=False,
    plot_bgcolor="#121a2b", paper_bgcolor="#121a2b",
    font=dict(size=14, color="#e6edf3"),
    title="Distribusi Persentase Kerawanan Banjir", title_x=0.5,
    xaxis_title="Kelas Kerawanan", yaxis_title="Persentase (%)",
    margin=dict(t=60, b=40),
)
fig_bar.update_traces(
    texttemplate="%{text:.2f}%", textposition="outside",
    marker_line_color="rgba(255,255,255,.4)", marker_line_width=1.2,
)

st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ==========================================================
# GRAFIK PIE
# ==========================================================

section_title("🥧 Proporsi Tiap Tingkat Kerawanan")

fig_pie = px.pie(
    df, names="Kelas", values="Persentase (%)", color="Kelas",
    color_discrete_map=warna, hole=0.5,
)
fig_pie.update_layout(
    template="plotly_dark", height=560,
    plot_bgcolor="#121a2b", paper_bgcolor="#121a2b",
    font=dict(color="#e6edf3"),
    title={"text": "Persentase Luas Tiap Tingkat Kerawanan", "x": 0.5},
    legend=dict(orientation="v", x=1.02, y=0.5),
    margin=dict(t=60, b=20),
)

st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ==========================================================
# PERSENTASE KERAWANAN PER DESA/KELURAHAN
# ==========================================================

section_title("📍 Persentase Tingkat Kerawanan Banjir per Desa/Kelurahan")

df_kel = hitung_statistik_per_kelurahan()

if df_kel.empty:
    st.warning("Data batas desa/kelurahan atau raster tidak ditemukan, grafik per desa tidak dapat ditampilkan.")
else:
    daftar_kelurahan = sorted(df_kel["Kelurahan"].unique())

    pilihan = st.multiselect(
        "Filter Desa/Kelurahan (kosongkan untuk menampilkan semua)",
        options=daftar_kelurahan,
        default=[],
        placeholder="Semua desa/kelurahan ditampilkan",
    )

    df_kel_tampil = df_kel[df_kel["Kelurahan"].isin(pilihan)] if pilihan else df_kel

    # Urutkan desa/kelurahan dari yang paling rawan ke paling aman,
    # berdasarkan skor tertimbang tiap kelas kerawanan (bukan alfabetis).
    bobot_kelas = {"Sangat Tinggi": 5, "Tinggi": 4, "Sedang": 3, "Rendah": 2, "Sangat Rendah": 1}
    pivot_kel = df_kel.pivot_table(index="Kelurahan", columns="Kelas", values="Persentase (%)", fill_value=0)
    skor_risiko = sum(pivot_kel.get(k, 0) * b for k, b in bobot_kelas.items())
    urutan_kelurahan = skor_risiko.sort_values(ascending=False).index.tolist()

    fig_kel = px.bar(
        df_kel_tampil,
        x="Kelurahan",
        y="Persentase (%)",
        color="Kelas",
        barmode="group",
        color_discrete_map=warna,
        category_orders={"Kelas": KELAS_URUTAN, "Kelurahan": urutan_kelurahan},
    )
    fig_kel.update_layout(
        template="plotly_dark", height=520,
        plot_bgcolor="#121a2b", paper_bgcolor="#121a2b",
        font=dict(size=13, color="#e6edf3"),
        title="Persentase Tingkat Kerawanan Banjir per Desa/Kelurahan", title_x=0.5,
        xaxis_title="Desa/Kelurahan", yaxis_title="Persentase (%)",
        legend_title_text="Tingkat Kerawanan",
        margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig_kel, use_container_width=True)
    st.caption(
        "Grafik menunjukkan proporsi luas tiap kelas kerawanan banjir di masing-masing desa/kelurahan, "
        "dihitung dari hasil klasifikasi Flood Index (zonal statistics)."
    )

st.markdown("---")

# ==========================================================
# TABEL STATISTIK
# ==========================================================

section_title("📋 Tabel Statistik Kerawanan")

df_tampil = df.copy()
df_tampil.columns = ["Kelas Kerawanan", "Jumlah Pixel", "Luas (Ha)", "Persentase (%)"]
df_tampil["Luas (Ha)"] = df_tampil["Luas (Ha)"].round(2)
df_tampil["Persentase (%)"] = df_tampil["Persentase (%)"].round(2)


def highlight(row):
    if row["Kelas Kerawanan"] == kelas_dominan:
        return ["background-color:#1565C0;color:white;font-weight:bold"] * len(row)
    return [""] * len(row)


st.dataframe(
    df_tampil.style.apply(highlight, axis=1),
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# ==========================================================
# INSIGHT & REKOMENDASI (dipadatkan — sebelumnya 3 bagian terpisah
# yang isinya saling tumpang tindih: Insight, Interpretasi, Kesimpulan)
# ==========================================================

section_title("💡 Insight & Rekomendasi")

low = df[df["Kelas"].isin(["Rendah", "Sangat Rendah"])]["Persentase (%)"].sum()
high = df[df["Kelas"].isin(["Tinggi", "Sangat Tinggi"])]["Persentase (%)"].sum()

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
        <div class="wg-card accent-p">
        <h4>📌 Temuan Utama</h4>
        <p>
        Kelas <b>{kelas_dominan}</b> mendominasi wilayah kajian dengan cakupan
        <b>{persentase_dominan:.2f}%</b> dari total luas. Secara umum,
        <b>{low:.1f}%</b> wilayah berada pada kategori rendah–sangat rendah,
        sementara <b>{high:.1f}%</b> wilayah berada pada kategori tinggi–sangat tinggi
        yang perlu mendapat perhatian khusus.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="wg-card accent-4">
        <h4>🎯 Rekomendasi</h4>
        <p>
        • Prioritaskan mitigasi pada area kelas Tinggi &amp; Sangat Tinggi.<br>
        • Perkuat sistem drainase pada zona kerawanan Sedang.<br>
        • Jadikan hasil ini dasar penyusunan tata ruang &amp; RTRW.<br>
        • Gunakan peta interaktif untuk identifikasi lokasi prioritas.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.page_link("pages/2_Peta.py", label="Lihat sebaran spasial di Peta Interaktif →", icon="🗺️")

footer(
    "WebGIS Analisis Kerawanan Banjir &middot; Kecamatan Tanah Sareal, Kota Bogor<br>"
    "Statistik dihitung dari hasil klasifikasi Flood Index &middot; Python, Pandas &amp; Plotly"
)
