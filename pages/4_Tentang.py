import streamlit as st
from utils.ui import load_css, page_header, section_title, param_card, flow_diagram, footer

load_css()

# =====================================================
# Hero
# =====================================================

page_header(
    eyebrow="Dokumentasi & Metodologi",
    title="Tentang Penelitian Ini",
    description=(
        "Halaman ini menjelaskan secara rinci metode analisis, parameter dan pembobotan, "
        "alur pengolahan data, sumber data, serta teknologi yang digunakan dalam membangun "
        "WebGIS Analisis Kerawanan Banjir Kecamatan Tanah Sareal."
    ),
    badges=["🎓 Teknik Informatika", "📍 Kota Bogor", "⚙️ Weighted Overlay"],
)

# =====================================================
# Tujuan Penelitian
# =====================================================

section_title("🎯 Tujuan Penelitian")

st.markdown(
    """
    - Mengidentifikasi tingkat kerawanan banjir di Kecamatan Tanah Sareal secara spasial.
    - Menghasilkan peta kerawanan banjir berbasis Sistem Informasi Geografis (SIG).
    - Mengembangkan aplikasi WebGIS sebagai media visualisasi hasil analisis yang mudah diakses publik.
    - Menyediakan informasi spasial yang dapat mendukung perencanaan tata ruang dan mitigasi bencana banjir.
    """
)

st.markdown("---")

# =====================================================
# Metode Analisis
# =====================================================

section_title("⚙️ Metode Analisis: Weighted Overlay")

st.markdown(
    """
    <div class="wg-card accent-p">
    <p>
    <b>Weighted Overlay</b> adalah metode analisis spasial yang menggabungkan beberapa parameter
    (layer raster) menjadi satu nilai indeks komposit, dengan memberikan bobot pada masing-masing
    parameter sesuai tingkat pengaruhnya terhadap potensi banjir. Semakin besar bobot suatu parameter,
    semakin besar pula pengaruhnya terhadap nilai akhir Flood Index.
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# =====================================================
# Parameter & Bobot
# =====================================================

section_title("🌧️ Parameter & Bobot Analisis")

st.caption("Setiap parameter direklasifikasi ke skala yang sama sebelum digabungkan sesuai bobotnya.")

p1, p2, p3, p4, p5 = st.columns(5)
with p1:
    param_card("🏔", "DEM (Elevasi)", 30, "#1a9850")
with p2:
    param_card("⛰", "Kemiringan Lereng", 20, "#91cf60")
with p3:
    param_card("🌧", "Curah Hujan", 20, "#ffd700")
with p4:
    param_card("🌊", "Jarak ke Sungai", 20, "#fc8d59")
with p5:
    param_card("🌿", "Tutupan Lahan", 10, "#d73027")

st.markdown("---")

# =====================================================
# Alur Kerja / Workflow
# =====================================================

section_title("🔄 Alur Pengolahan Data")

flow_diagram([
    ("📥", "Data Spasial"),
    ("🛠️", "Pre-processing"),
    ("🧮", "Weighted Overlay"),
    ("📊", "Flood Index"),
    ("🗺️", "Flood Class"),
    ("🌍", "WebGIS"),
])

with st.expander("Lihat tahapan lebih rinci"):
    st.markdown(
        """
        1. **Pengumpulan data spasial** — DEM, kemiringan lereng, curah hujan, jaringan sungai, dan tutupan lahan.
        2. **Pre-processing** — penyeragaman sistem koordinat, resolusi, dan cakupan wilayah (clip ke batas kecamatan).
        3. **Reklasifikasi** — setiap parameter diberi skor 1–5 berdasarkan tingkat pengaruhnya terhadap banjir.
        4. **Pembobotan & Overlay** — seluruh parameter digabungkan menggunakan metode Weighted Overlay sesuai bobot masing-masing.
        5. **Flood Index** — dihasilkan nilai indeks kerawanan banjir kontinu untuk seluruh wilayah kajian.
        6. **Klasifikasi (Flood Class)** — indeks dikelompokkan menjadi 5 kelas: Sangat Rendah hingga Sangat Tinggi.
        7. **Publikasi WebGIS** — hasil ditampilkan pada peta interaktif, statistik, dan dokumentasi ini.
        """
    )

st.markdown("---")

# =====================================================
# Sumber Data
# =====================================================

section_title("🗂️ Sumber Data")

st.dataframe(
    {
        "Parameter": ["DEM (Elevasi)", "Kemiringan Lereng", "Curah Hujan", "Jarak ke Sungai", "Tutupan Lahan"],
        "Sumber Data": ["NASA SRTM", "Turunan DEM SRTM", "CHIRPS", "OpenStreetMap", "ESA WorldCover"],
    },
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# =====================================================
# Teknologi
# =====================================================

section_title("💻 Teknologi yang Digunakan")

t1, t2, t3 = st.columns(3)
with t1:
    st.markdown(
        """
        <div class="wg-card accent-1">
        <h4>🐍 Pengolahan Data</h4>
        <p>Python &middot; Pandas &middot; NumPy &middot; GeoPandas &middot; Rasterio</p>
        </div>
        """, unsafe_allow_html=True)
with t2:
    st.markdown(
        """
        <div class="wg-card accent-2">
        <h4>🌍 Visualisasi Peta</h4>
        <p>Streamlit &middot; Folium &middot; Streamlit-Folium &middot; Branca</p>
        </div>
        """, unsafe_allow_html=True)
with t3:
    st.markdown(
        """
        <div class="wg-card accent-3">
        <h4>📈 Visualisasi Data</h4>
        <p>Plotly Express &middot; Matplotlib &middot; GeoJSON</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# Output & Manfaat
# =====================================================

col1, col2 = st.columns(2)

with col1:
    section_title("📦 Output Penelitian")
    st.markdown(
        """
        <div class="wg-card accent-p">
        <p>
        • Flood Index (indeks kerawanan banjir kontinu)<br>
        • Flood Class (5 kelas kerawanan)<br>
        • Peta interaktif berbasis web<br>
        • Statistik distribusi luas &amp; persentase<br>
        • Dokumentasi metodologi penelitian
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    section_title("🎯 Manfaat Penelitian")
    st.markdown(
        """
        <div class="wg-card accent-1">
        <p>
        • Dasar mitigasi bencana banjir<br>
        • Perencanaan tata ruang wilayah<br>
        • Identifikasi kawasan prioritas penanganan<br>
        • Pengambilan keputusan berbasis data spasial<br>
        • Media pembelajaran Sistem Informasi Geografis
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# =====================================================
# Footer / Kredit
# =====================================================

section_title("🏛️ Informasi Penelitian")

st.markdown(
    """
    <div class="wg-card accent-p">
    <p>
    <b>Judul</b> &nbsp;: Analisis Kerawanan Banjir Kecamatan Tanah Sareal Menggunakan Metode Weighted Overlay Berbasis SIG<br>
    <b>Program Studi</b> &nbsp;: Teknik Informatika<br>
    <b>Lokasi Kajian</b> &nbsp;: Kecamatan Tanah Sareal, Kota Bogor<br>
    <b>Metode</b> &nbsp;: Weighted Overlay (5 parameter spasial)
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)

footer(
    "WebGIS Analisis Kerawanan Banjir &middot; Kecamatan Tanah Sareal, Kota Bogor<br>"
    "Dibangun menggunakan Python, Streamlit, Folium, GeoPandas, Rasterio &amp; Plotly"
)
