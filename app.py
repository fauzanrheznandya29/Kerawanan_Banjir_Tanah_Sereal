import streamlit as st
from utils.ui import load_css, sidebar_brand, sidebar_footer

st.set_page_config(
    page_title="WebGIS Kerawanan Banjir | Tanah Sareal",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Gaya global (CSS) + branding sidebar — berlaku untuk SEMUA halaman
# karena dijalankan sekali di sini sebelum halaman aktif dirender.
load_css()
sidebar_brand()

# ===============================
# Navigation
# ===============================

pg = st.navigation(
    [
        st.Page(
            "pages/1_Beranda.py",
            title="Beranda",
            icon="🏠",
            default=True,
        ),
        st.Page(
            "pages/2_Peta.py",
            title="Peta Interaktif",
            icon="🗺️",
        ),
        st.Page(
            "pages/3_Statistik.py",
            title="Statistik",
            icon="📊",
        ),
        st.Page(
            "pages/4_Tentang.py",
            title="Tentang",
            icon="ℹ️",
        ),
    ]
)

pg.run()

# Footer sidebar dirender setelah menu navigasi bawaan Streamlit
sidebar_footer()
