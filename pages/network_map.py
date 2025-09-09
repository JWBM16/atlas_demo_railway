import os
import folium
import streamlit as st
import streamlit.components.v1 as components

from folium.plugins import Draw, Fullscreen, Geocoder, PolyLineTextPath
from PIL import Image
from streamlit_folium import st_folium
from datetime import datetime, timedelta
from session_manager import is_session_active, load_session, logout, save_session

st.set_page_config(layout="wide")

# ==============================
# atlas.io Version 1.2.0 - Copyright © White Labs Technologies 2025
# author: Jhonattan W. Blanco
# ==============================


session = load_session()

if not is_session_active():
    st.warning("🔒 Tu sesión ha expirado o no está activa.")
    st.stop()

elapsed = datetime.now() - session["start_time"]
remaining = timedelta(minutes=5) - elapsed
minutes, seconds = divmod(int(remaining.total_seconds()), 60)
progress = min(elapsed.total_seconds() / 300, 1.0)

current_dir = os.path.dirname(os.path.abspath(__file__))
pop_path = os.path.join(current_dir, "assets_2", "pop_icon.png")

html_atlas = """
<div style="
    background-color: white;
    color: black;
    font-family: Tahoma, sans-serif;
    font-weight: bold;
    font-size: 32px;
    text-transform: lowercase;
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 12px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    width: fit-content;">
    atlas.io&nbsp;🌐
</div>
"""


left_co, center_co, last_co = st.columns(3)
with left_co:
    st.markdown(html_atlas, unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: left; color: white;'>NETWORK MAP</h3>",
        unsafe_allow_html=True,
    )


nm = folium.Map(
    location=[25.782428653711648, -80.19311895444139],
    tiles="OpenStreetMap",
    zoom_start=3,
)

# Marker: Equinix MIA
folium.Marker(
    [25.782428653711648, -80.19311895444139],
    popup="Equinix Miami NAP",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(40, 40)),
    tooltip="Equinix Miami NAP",
).add_to(nm)

# Marker Cirion CCS
folium.Marker(
    [10.493001773525164, -66.80715724563946],
    popup="Cirion Caracas",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Cirion Caracas",
).add_to(nm)

# Marker: GTD Barranquilla
folium.Marker(
    [11.805890683733363, -74.8413277718902],
    popup="GTD Barranquilla",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="GTD Barranquilla",
).add_to(nm)


# Marker: GTD Data Center Surco
folium.Marker(
    [-12.124163722497183, -76.97758772055207],
    popup="GTD Data Center Surco",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="GTD Data Center Surco",
).add_to(nm)

# Marker: Equinix BG1
folium.Marker(
    [4.671201469510356, -74.16163246001159],
    popup="Equinix BG1",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix BG1",
).add_to(nm)

# Marker: Equinix SP3
folium.Marker(
    [-23.466198286224852, -46.86303046779228],
    popup="Equinix SP3",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix SP3",
).add_to(nm)


# Marker: GTD Santiago Panamericana
folium.Marker(
    [-33.396185035166205, -70.68465317435454],
    popup="GTD Santiago Panamericana",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="GTD Santiago Panamericana",
).add_to(nm)

# Marker: IFX Networks Buenos Aires
folium.Marker(
    [-34.613699692214766, -58.38848434883733],
    popup="IFX Networks Buenos Aires",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="IFX Networks Buenos Aires",
).add_to(nm)

# Marker: KIO PA1 Panama
folium.Marker(
    [8.91975718862525, -79.59369500891646],
    popup="KIO PA1 Panama",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="KIO PA1 Panama",
).add_to(nm)

# ------------------------------------------------------------#

# Line MIA - CCS
mia_ccs = [
    [25.782428653711648, -80.19311895444139],
    [10.493001773525164, -66.80715724563946],
]

mia_ccs_line = folium.PolyLine(
    [mia_ccs],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_ccs_line,
    "            10GB Prisma MRC:$ 0.00",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line Miami - Barranquilla
mia_barranquilla = [
    [25.782428653711648, -80.19311895444139],
    [11.805890683733363, -74.8413277718902],
]

mia_barranquilla_line = folium.PolyLine(
    [mia_barranquilla],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_barranquilla_line,
    "            Prisma",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA - GTD Surco
mia_surco = [
    [25.782428653711648, -80.19311895444139],
    [-12.124163722497183, -76.97758772055207],
]

mia_surco_line = folium.PolyLine(
    [mia_surco],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_surco_line,
    "          1GB ",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line MIA - Equinix BG1
mia_bog1 = [
    [25.782428653711648, -80.19311895444139],
    [4.671201469510356, -74.16163246001159],
]

mia_bog1_line = folium.PolyLine(
    [mia_bog1],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_bog1_line,
    "                        10GB Prisma",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA - EquinixSP3
mia_sp3 = [
    [25.782428653711648, -80.19311895444139],
    [-23.466198286224852, -46.86303046779228],
]

mia_sp3_line = folium.PolyLine(
    [mia_sp3],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_sp3_line,
    "                        10GB Prisma",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA - GTD Panamericana Santiago
mia_stgo = [
    [25.782428653711648, -80.19311895444139],
    [-33.396185035166205, -70.68465317435454],
]

mia_stgo_line = folium.PolyLine(
    [mia_stgo],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_stgo_line,
    "                      2 x 10GB Prisma",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA- BSAS
mia_bsas = [
    [25.782428653711648, -80.19311895444139],
    [-34.613699692214766, -58.38848434883733],
]

mia_bsas_line = folium.PolyLine(
    [mia_bsas],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_bsas_line,
    "                       Prisma",
    offset=-5,
    attributes=attr,
).add_to(nm)

Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(nm)


map_html = nm._repr_html_()

# Combinar todo en un solo bloque
final_html = f"""
<style>
.map-container {{
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    width: 90%;
    height: 90%;
    position: relative;
}}

/* Aplica también a los hijos */
.map-container iframe,
.map-container .folium-map,
.map-container > div {{
    border-radius: 20px !important;
    overflow: hidden;
}}
</style>
<div class="map-container">
    {map_html}
</div>
"""


# Mostrar en Streamlit
components.html(final_html, height=1000)

with st.sidebar:
    st.success(f"Bienvenido: {session['username']}")
    st.markdown(f"**Tiempo restante:** {minutes} min {seconds} seg")
    st.progress(progress, text=f"{int(progress * 100)}% usado")

    # Botones siempre disponibles en la barra lateral
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reiniciar sesión"):
            session["start_time"] = datetime.now()
            save_session(session)
            st.rerun()
    with col2:
        if st.button("🚪 Cerrar sesión"):
            logout()
            st.rerun()
with st.sidebar:
    # Espaciador flexible
    for _ in range(13):
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Footer
    st.sidebar.markdown(
        """
            <hr style='border: none; height: 1px; background-color: #555; margin-top: 15px; margin-bottom: 10px;'>

            <div style='text-align: center; color: white; font-size: 11px; line-height: 1.4; font-family: Tahoma, sans-serif;'>
                &copy; 2025 White Labs Technologies. All rights reserved.<br>
                Version 1.2.0
            </div>
            """,
        unsafe_allow_html=True,
    )
