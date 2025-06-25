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

    # st.image(orchest_img, width=230)
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

# Marker: Equinix 1950 N Stemmon
folium.Marker(
    [32.80103401394068, -96.81953367343844],
    popup="Equinix Dallas, TX",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix Dallas, TX",
).add_to(nm)


# Marker: KIO Tultitlan
folium.Marker(
    [19.627981744365865, -99.14865786775525],
    popup="KIO Tultitlan",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="KIO Tultitlan",
).add_to(nm)

# Marker: Equinix BG1
folium.Marker(
    [4.671201469510356, -74.16163246001159],
    popup="Equinix BG1",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix BG1",
).add_to(nm)

# Marker: Cirion Peru
folium.Marker(
    [-12.088901062099541, -76.97322267180107],
    popup="Cirion Peru",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Cirion Peru",
).add_to(nm)

# Marker: CoreSite LA1
folium.Marker(
    [34.048107635076434, -118.25569304871244],
    popup="CoreSite LA1",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="CoreSite LA1",
).add_to(nm)

# Marker: ATC Tijuana POP
folium.Marker(
    [32.51366954699249, -117.00987511278693],
    popup="ATC Tijuana POP",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="ATC Tijuana POP",
).add_to(nm)

# Marker: Digital Realty NYC
folium.Marker(
    [40.72065311686489, -74.0045701804981],
    popup="Digital Realty NYC",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Digital Realty NYC",
).add_to(nm)

# Marker: Equinix SP4
folium.Marker(
    [-23.493378933158176, -46.80943088893639],
    popup="Equinix SP4",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix SP4",
).add_to(nm)

# Marker: Equinix SP3
folium.Marker(
    [-23.466198286224852, -46.86303046779228],
    popup="Equinix SP3",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix SP3",
).add_to(nm)


# Marker: Torre Entel Santiago
folium.Marker(
    [-33.44459693811853, -70.65609065572966],
    popup="Torre Entel Santiago",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Torre Entel SP4",
).add_to(nm)


# Marker: Powerhost Santiago
folium.Marker(
    [-33.447756497929525, -70.61987913729631],
    popup="Power Host",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Power Host",
).add_to(nm)


# Marker: Cirion Santiago
folium.Marker(
    [-33.357978698742784, -70.675778746297371],
    popup="Cirion Santiago",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Cirion Santiago",
).add_to(nm)

# Marker: Cirion Buenos Aires
folium.Marker(
    [-34.575489980020365, -58.46845950135029],
    popup="Cirion Santiago",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Cirion Buenos aires",
).add_to(nm)

# Marker: Equinix Ashburn DC3
folium.Marker(
    [39.0223542918074, -77.46090914631269],
    popup="Equinic DC3 - Ashburn",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinic DC3 - Ashburn",
).add_to(nm)

# Marker: Cirion Corazal
folium.Marker(
    [8.9749524953744, -79.56637803429211],
    popup="Cirion Corazal",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Cirion Corazal",
).add_to(nm)

# Marker: Equinix TY8
folium.Marker(
    [35.622193698029314, 139.74789702363194],
    popup="Equinix TY8",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="Equinix TY8",
).add_to(nm)

# Marker: MegaPlus Hong Kong
folium.Marker(
    [22.29355335611981, 114.27406707981986],
    popup="MEGA+ Hong Kong",
    icon=folium.features.CustomIcon(icon_image=pop_path, icon_size=(45, 45)),
    tooltip="MEGA+ Hong Kong",
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
    "          10GB ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA - Dallas, TX
mia_dallas = [
    [25.782428653711648, -80.19311895444139],
    [32.80103401394068, -96.81953367343844],
]

mia_dallas_line = folium.PolyLine(
    [mia_dallas],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_dallas_line,
    "            10GB Sprint 33ms MRC:$ 3,500",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line KIO Tultitlan - Dallas, TX
kio_dallas = [
    [19.627981744365865, -99.14865786775525],
    [32.80103401394068, -96.81953367343844],
]

kio_dallas_line = folium.PolyLine(
    [kio_dallas],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    kio_dallas_line,
    "            5GB IENTC",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA - Equinix BG1
mia_bg1 = [
    [25.782428653711648, -80.19311895444139],
    [4.671201469510356, -74.16163246001159],
]

mia_bg1_line = folium.PolyLine(
    [mia_bg1],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_bg1_line,
    "          1GB ",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line MIA - Cirion Peru
mia_lima = [
    [25.782428653711648, -80.19311895444139],
    [-12.088901062099541, -76.97322267180107],
]

mia_lima_line = folium.PolyLine(
    [mia_lima],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_lima_line,
    "                        10GB Cirion",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Coresite - kio
coresite_kio = [
    [34.048107635076434, -118.25569304871244],
    [19.627981744365865, -99.14865786775525],
]

coresite_kio_line = folium.PolyLine(
    [coresite_kio],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    coresite_kio_line,
    "                        10GB Cirion",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Coresite - ATC Tijuana
coresite_atc = [
    [34.048107635076434, -118.25569304871244],
    [32.51366954699249, -117.00987511278693],
]

coresite_atc_line = folium.PolyLine(
    [coresite_atc],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    coresite_atc_line,
    "                      2 x 10GB Vivaro",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line NYC - MIA NAP
nyc_mia = [
    [40.72065311686489, -74.0045701804981],
    [25.782428653711648, -80.19311895444139],
]

nyc_mia_line = folium.PolyLine(
    [nyc_mia],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    nyc_mia_line,
    "                       WindStream",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line MIA NAP - SP4
mia_sp4 = [
    [-23.493378933158176, -46.80943088893639],
    [-26.35442786294854, -43.0302560263052],
    [-24.753112188967613, -33.914493954233045],
    [-4.805431057619375, -29.901000697208012],
    [25.782428653711648, -80.19311895444139],
]

mia_sp4_line = folium.PolyLine(
    [mia_sp4],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    mia_sp4_line,
    "          10GB ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Torre Entel - PowrHost
entel_power = [
    [-33.447756497929525, -70.61987913729631],
    [-33.44459693811853, -70.65609065572966],
]

entel_power_line = folium.PolyLine(
    [entel_power],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    entel_power_line,
    "                       10GB",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line PowrHost - SP4
power_sp4 = [
    [-23.493378933158176, -46.80943088893639],
    [-33.447756497929525, -70.61987913729631],
]

power_sp4_line = folium.PolyLine(
    [power_sp4],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    power_sp4_line,
    "                       10GB Powerhost 54ms protected",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line PowrHost - Cirion Santiago
power_cirioncl = [
    [-33.447756497929525, -70.61987913729631],
    [-33.357978698742784, -70.675778746297371],
]

power_cirioncl_line = folium.PolyLine(
    [power_cirioncl],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    power_sp4_line,
    "                       10GB Powerhost 54ms protected",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Cirion Buenos Aires - Cirion Santiago
cirionbs_cirioncl = [
    [-33.357978698742784, -70.675778746297371],
    [-34.575489980020365, -58.46845950135029],
]

cirionbs_cirioncl_line = folium.PolyLine(
    [cirionbs_cirioncl],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    cirionbs_cirioncl_line,
    "                       10GB Malbec 27ms",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Cirion Buenos Aires - SP3
cirionbs_sp3 = [
    [-34.575489980020365, -58.46845950135029],
    [-23.466198286224852, -46.86303046779228],
]

cirionbs_sp3_line = folium.PolyLine(
    [cirionbs_sp3],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    cirionbs_sp3_line,
    "                       10GB Malbec 27ms",
    offset=-5,
    attributes=attr,
).add_to(nm)


# Line NYC - DC3 - Ashburn
nyc_dc3 = [
    [39.0223542918074, -77.46090914631269],
    [40.72065311686489, -74.0045701804981],
]

nyc_dc3_line = folium.PolyLine(
    [nyc_dc3],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    nyc_dc3_line,
    "                       10GB Sprint 5.54ms",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line NYC - Coresite_la1
nyc_coresite_la1 = [
    [34.048107635076434, -118.25569304871244],
    [40.72065311686489, -74.0045701804981],
]

nyc_coresite_la1_line = folium.PolyLine(
    [nyc_coresite_la1],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    nyc_coresite_la1_line,
    "                       10GB Sprint 56ms",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Dallas - Coresite_la1
dallas_coresite_la1 = [
    [34.048107635076434, -118.25569304871244],
    [32.80103401394068, -96.81953367343844],
]

dallas_coresite_la1_line = folium.PolyLine(
    [dallas_coresite_la1],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    dallas_coresite_la1_line,
    "                       10GB Sprint 56ms",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Torre Entel - Coresite_la1
torre_entel_coresite_la1 = [
    [34.048107635076434, -118.25569304871244],
    [-33.44459693811853, -70.65609065572966],
]

torre_entel_coresite_la1_line = folium.PolyLine(
    [torre_entel_coresite_la1],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    dallas_coresite_la1_line,
    "                                        1GB Curie RTD 106ms                    ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line SP4 - Miami NAP
sp4_miami_nap = [
    [25.782428653711648, -80.19311895444139],
    [-23.493378933158176, -46.80943088893639],
]

sp4_miami_nap_line = folium.PolyLine(
    [sp4_miami_nap],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    sp4_miami_nap_line,
    "                                        1GB Curie RTD 106ms                    ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line SP4 - NYC
sp4_nyc = [
    [-23.493378933158176, -46.80943088893639],
    [-26.14666310224416, -31.634615974216672],
    [-9.48967567872335, -25.52376706643535],
    [40.72065311686489, -74.0045701804981],
]

sp4_nyc_line = folium.PolyLine(
    [sp4_nyc],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    sp4_nyc_line,
    "                                        1GB Globenet                    ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line SP4 - NYC
sp4_nyc_seabras = [
    [-23.493378933158176, -46.80943088893639],
    [40.72065311686489, -74.0045701804981],
]

sp4_nyc_seabras_line = folium.PolyLine(
    [sp4_nyc_seabras],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    sp4_nyc_seabras_line,
    "                                        10GB Seabras                    ",
    offset=-5,
    attributes=attr,
).add_to(nm)

# Line Cirion Corazal - Miami NAP
sp4_nyc_seabras = [
    [8.9749524953744, -79.56637803429211],
    [25.782428653711648, -80.19311895444139],
]

sp4_nyc_seabras_line = folium.PolyLine(
    [sp4_nyc_seabras],
).add_to(nm)
attr = {"fill": "#007DEF", "font-weight": "bold", "font-size": "14"}
folium.plugins.PolyLineTextPath(
    sp4_nyc_seabras_line,
    "                                        10GB Seabras                    ",
    offset=-5,
    attributes=attr,
).add_to(nm)


Fullscreen(
    position="topright",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(nm)


# call to render Folium map in Streamlit
# st_data = st_folium(
#     nm, width=1000, height=500, returned_objects=["last_object_clicked"]
# )
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
