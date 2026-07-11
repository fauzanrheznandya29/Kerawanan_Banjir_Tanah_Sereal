import streamlit as st
import pandas as pd
from utils.ui import load_css, page_header, section_title, nav_card, footer

load_css()

# =====================================================
# Data ringkas (dibaca dari hasil analisis untuk angka yang akurat)
# =====================================================

df = pd.read_csv("data/statistik/Statistik_Kerawanan_Banjir.csv")
total_luas = df["Luas (ha)"].sum()
kelas_dominan = df.loc[df["Persentase (%)"].idxmax(), "Kelas"]
persentase_dominan = df["Persentase (%)"].max()

# =====================================================
# Hero
# =====================================================

page_header(
    eyebrow="WebGIS · Kecamatan Tanah Sareal, Kota Bogor",
    title="Pemetaan Kerawanan Banjir Berbasis SIG",
    description=(
        "Platform visualisasi spasial interaktif untuk memantau tingkat kerawanan banjir "
        "di Kecamatan Tanah Sareal. Dibangun dari hasil analisis spasial <b>Weighted Overlay</b> "
        "terhadap lima parameter fisik wilayah, dan disajikan dalam bentuk peta, statistik, "
        "serta dokumentasi metode yang dapat ditelusuri."
    ),
    badges=["🗺️ Peta Interaktif", "📊 Statistik Real-time", "⚙️ Weighted Overlay", "🌧️ 5 Parameter"],
)

# =====================================================
# Ringkasan cepat wilayah
# =====================================================

section_title("Ringkasan Wilayah Kajian")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Luas Wilayah", f"{total_luas:,.2f} Ha")
c2.metric("Kelas Kerawanan Dominan", kelas_dominan, f"{persentase_dominan:.1f}% area")
c3.metric("Jumlah Parameter", "5")
c4.metric("Metode Analisis", "Weighted Overlay")

st.caption(
    "Angka di atas dihitung langsung dari hasil klasifikasi indeks kerawanan banjir. "
    "Rincian distribusi tiap kelas dapat dilihat di halaman **Statistik**."
)

st.write("")

# =====================================================
# Akses cepat ke halaman lain
# =====================================================

section_title("Jelajahi Aplikasi")

col1, col2, col3 = st.columns(3)

with col1:
    nav_card(
        "🗺️",
        "Peta Interaktif",
        "Eksplorasi peta kerawanan banjir dengan pilihan basemap, kontrol layer, "
        "legenda, dan alat ukur — lengkap seperti WebGIS profesional.",
        "pages/2_Peta.py",
        "Buka Peta",
    )

with col2:
    nav_card(
        "📊",
        "Statistik Kerawanan",
        "Lihat distribusi luas dan persentase tiap kelas kerawanan banjir "
        "dalam bentuk grafik dan tabel interaktif.",
        "pages/3_Statistik.py",
        "Lihat Statistik",
    )

with col3:
    nav_card(
        "ℹ️",
        "Tentang & Metodologi",
        "Pelajari metode Weighted Overlay, bobot tiap parameter, sumber data, "
        "serta teknologi yang digunakan dalam penelitian ini.",
        "pages/4_Tentang.py",
        "Baca Selengkapnya",
    )

st.write("")
st.markdown("---")

# =====================================================
# Teaser singkat (bukan penjelasan lengkap — detail ada di Tentang)
# =====================================================

left, right = st.columns([2, 1])

with left:
    section_title("Tentang Aplikasi Ini")
    st.markdown(
        """
        Aplikasi ini dikembangkan sebagai media visualisasi hasil penelitian kerawanan banjir,
        yang menggabungkan lima parameter fisik wilayah — **DEM, kemiringan lereng, curah hujan,
        jarak terhadap sungai, dan tutupan lahan** — menjadi satu indeks kerawanan menggunakan
        metode **Weighted Overlay**.

        Hasil analisis kemudian diklasifikasikan ke dalam lima tingkat kerawanan, mulai dari
        *Sangat Rendah* hingga *Sangat Tinggi*, dan ditampilkan secara spasial pada peta interaktif
        untuk mendukung upaya mitigasi dan perencanaan tata ruang di wilayah rawan banjir.
        """
    )
    st.page_link("pages/4_Tentang.py", label="Lihat metodologi lengkap →", icon="ℹ️")

with right:
    st.markdown(
        """
        <div class="wg-card accent-p">
            <h4>📦 Empat Menu Utama</h4>
            <p>
            🏠 <b>Beranda</b> — ringkasan & akses cepat<br><br>
            🗺️ <b>Peta</b> — visualisasi spasial interaktif<br><br>
            📊 <b>Statistik</b> — distribusi kelas kerawanan<br><br>
            ℹ️ <b>Tentang</b> — metode, data, dan teknologi
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

footer(
    "WebGIS Analisis Kerawanan Banjir &middot; Kecamatan Tanah Sareal, Kota Bogor<br>"
    "Dibangun dengan Python, Streamlit, Folium, GeoPandas &amp; Rasterio"
)
