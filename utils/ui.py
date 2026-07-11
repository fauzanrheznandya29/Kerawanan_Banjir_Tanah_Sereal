"""
Komponen UI bersama agar tampilan Beranda, Peta, Statistik, dan Tentang konsisten.
Referensi gaya diambil dari palet warna & nuansa halaman Peta (biru tua/kartu gelap).
"""

from pathlib import Path
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def load_css():
    """Suntikkan CSS global. Aman dipanggil berkali-kali (idempotent)."""
    css_path = ASSETS_DIR / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def sidebar_brand():
    """Header branding di atas menu sidebar bawaan Streamlit, menggantikan tampilan template polos."""
    st.sidebar.markdown(
        """
        <div class="wg-sidebar-brand">
            <div class="logo">🌊</div>
            <div>
                <div class="title">FloodRisk&nbsp;Tanah&nbsp;Sareal</div>
                <div class="subtitle">WebGIS Kerawanan Banjir</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_footer():
    """Info ringkas di bagian bawah sidebar (di bawah daftar menu)."""
    st.sidebar.markdown(
        """
        <div class="wg-sidebar-footer">
            <b>Wilayah Kajian</b><br>Kec. Tanah Sareal, Kota Bogor<br><br>
            <b>Metode</b><br>Weighted Overlay (5 parameter)
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, description: str, badges=None):
    """Hero banner konsisten untuk setiap halaman (mengacu pada gaya visual halaman Peta)."""
    badges = badges or []
    badges_html = "".join(f'<span class="wg-badge">{b}</span>' for b in badges)
    st.markdown(
        f"""
        <div class="wg-hero">
            <span class="eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            <p>{description}</p>
            <div class="badges">{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str):
    st.markdown(
        f"""
        <div class="wg-section-title">
            <div class="bar"></div>
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def nav_card(icon: str, title: str, desc: str, target_page: str, link_label: str):
    """Kartu akses cepat di Beranda yang menautkan ke halaman lain (Peta/Statistik/Tentang)."""
    st.markdown(
        f"""
        <div class="wg-navcard">
            <div class="ic">{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link(target_page, label=link_label, icon="👉")


def param_card(icon: str, name: str, weight: int, color: str):
    st.markdown(
        f"""
        <div class="wg-param-card">
            <div class="ic">{icon}</div>
            <div class="name">{name}</div>
            <div class="weight" style="color:{color};">{weight}%</div>
            <div class="bar"><div style="width:{weight}%;background:{color};"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def flow_diagram(steps):
    """steps: list of (icon, label)"""
    parts = []
    for i, (icon, label) in enumerate(steps):
        parts.append(f'<div class="step"><span class="ic">{icon}</span>{label}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="arrow">➜</div>')
    st.markdown(f'<div class="wg-flow">{"".join(parts)}</div>', unsafe_allow_html=True)


def footer(text: str):
    st.markdown(f'<div class="wg-footer">{text}</div>', unsafe_allow_html=True)
