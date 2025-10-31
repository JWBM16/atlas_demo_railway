import time
import json
import os
import math
import polars as pl
import sqlite3
import unicodedata
import random
import flag
import folium
import geopandas
import pandas as pd
import smtplib
import unidecode
import streamlit as st
import streamlit.components.v1 as components
import streamlit_antd_components as sac
import data_sheet as dt
from session_manager import (
    init_session,
    VALID_USERS,
    is_session_active,
    start_auth_flow,
    verify_code,
    logout,
    load_session,
    save_session,
    stop_if_session_expired,
)
from datetime import datetime, timedelta
from email.message import EmailMessage
from dotenv import load_dotenv
from streamlit_folium import st_folium
from folium.plugins import Draw, Fullscreen, Geocoder, PolyLineTextPath
from folium import Marker
from folium.plugins import MarkerCluster
from folium.features import DivIcon
from folium import Tooltip
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from PIL import Image
from data_sheet import (
    super_1,
    super_2,
    super_3,
)

# ==============================
# atlas.io Version 1.2.0 - Copyright © White Labs Technologies 2025
# author: Jhonattan W. Blanco
# ==============================


# --- 1️⃣ Función de notificación ----------------------
def notificacion_js_un_minuto():
    js = """
    <script>
    if (Notification.permission !== "granted") {
      Notification.requestPermission();
    }
    setTimeout(function() {
      if (Notification.permission === "granted") {
        new Notification("⏱️ Queda 1 minuto", {
          body: "Tu sesión expirará en 1 minuto.",
        });
      } else {
        alert("Tu sesión expirará en 1 minuto.");
      }
    }, 1000);
    </script>
    """
    components.html(js)


st.set_page_config(layout="wide")
init_session()

# Verifica expiración de sesión y detiene si es necesario
stop_if_session_expired()


# Cargar variables de entorno
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ==================================

current_dir = os.path.dirname(os.path.abspath(__file__))


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


session = load_session()


def agregar_marcadores_con_estilo(geo_df, mapa):
    """Agrega CircleMarkers con Tooltips permanentes y Popups sin imágenes."""

    COLOR_MAP = {"EPL": "blue", "DIA": "red"}

    for _, row in geo_df.iterrows():
        # Preparar datos básicos
        service = str(row.get("SERVICE", "")).strip().upper()
        color = COLOR_MAP.get(service, "green")

        try:
            bandwidth_val = float(str(row.get("BANDWIDTH", "0")).replace(",", ""))
            bandwidth = f"{int(bandwidth_val)} Mbps"
        except ValueError:
            bandwidth = "N/A"

        try:
            mrc_val = float(str(row.get("MRC", "0")).replace("$", "").replace(",", ""))
            mrc = f"${int(mrc_val):,}"
        except ValueError:
            mrc = "N/A"

        term = row.get("TERM", "N/A")
        term = int(term) if str(term).isdigit() else "N/A"

        texto_tooltip = f"{bandwidth} {mrc} ({term})"

        # Estilo dinámico
        length = len(texto_tooltip)
        if length < 25:
            tooltip_direction, tooltip_offset, font_size = "right", (10, 0), "11px"
        elif length <= 35:
            tooltip_direction, tooltip_offset, font_size = "top", (0, -10), "10px"
        else:
            tooltip_direction, tooltip_offset, font_size = "top", (0, -10), "9px"

        tooltip_html = folium.Tooltip(
            f"""
            <div style="font-size:{font_size}; font-weight:bold; font-family:Arial; color:darkblue; text-align:center;">
                {bandwidth}<br>{mrc} ({term})
            </div>
            """,
            permanent=True,
            direction=tooltip_direction,
            offset=tooltip_offset,
        )

        # Popup informativo
        popup_html = f"""
            <div style="font-family: Arial; font-size: 14px; text-align: center;">
                <h4><b>{service}</b></h4>
                <p><b>Velocidad:</b> {bandwidth}</p>
                <p><b>Proveedor:</b> {row.get('PROVIDER', '')}</p>
                <p><b>Dirección:</b> {row.get('ADDRESS', '')}</p>
                <p><b>País:</b> {row.get('COUNTRY', '')}</p>
                <p><b>Ciudad:</b> {row.get('CITY', '')}</p>
                <p><b>Precio MRC:</b> {mrc}</p>
                <p><b>Precio NRC:</b> {row.get('NRC', '')}</p>
                <p><b>Term:</b> {term} meses</p>
                <p><b>Fecha:</b> {row.get('DATE', '')}</p>
                <p><b>Comentarios:</b> {row.get('COMMENTS', '')}</p>
                <p><b>Opportunity:</b> {row.get('OPPORTUNITY', '')}</p>
                <p><b>Coordenadas:</b> {row.get('LATITUDE')}, {row.get('LONGITUDE')}</p>
            </div>
        """

        popup = folium.Popup(popup_html, max_width=300)

        folium.CircleMarker(
            location=[row.get("LATITUDE"), row.get("LONGITUDE")],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=tooltip_html,
            popup=popup,
        ).add_to(mapa)

    return mapa


def agregar_marcadores_clusterizados(df, mapa, separacion_metros=30):
    # Crear FeatureGroup con nombre visible en el LayerControl
    hg = folium.FeatureGroup(name="Costs by provider", show=True).add_to(mapa)

    # Crear cluster dentro del FeatureGroup
    cluster = MarkerCluster(name="Provider Cluster").add_to(hg)

    R = 6371000  # Radio de la Tierra en metros

    for i, (_, row) in enumerate(df.iterrows()):
        lat0 = math.radians(row["LATITUDE"])
        lon0 = math.radians(row["LONGITUDE"])

        # Generamos un ángulo único para cada marcador
        angle_rad = (2 * math.pi / len(df)) * i

        # Desplazamiento en metros convertido a latitud/longitud
        delta_lat = (separacion_metros / R) * math.cos(angle_rad)
        delta_lon = (separacion_metros / (R * math.cos(lat0))) * math.sin(angle_rad)

        lat = math.degrees(lat0 + delta_lat)
        lon = math.degrees(lon0 + delta_lon)

        # Info tooltip
        tooltip_html = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>PROVIDER:</b> {row['PROVIDER']}<br>
                <b>SERVICE:</b> {row['SERVICE']}<br>
                <b>BANDWIDTH:</b> {row['BANDWIDTH']} Mbps<br>
                <b>MRC:</b> {row['MRC']}<br>
                <b>NRC:</b> {row['NRC']}<br>
                <b>TERM:</b> {row['TERM']} meses<br>
                <b>OPPORTUNITY:</b> {row.get("OPPORTUNITY", "")}<br>
                <b>COUNTRY:</b> {row.get("COUNTRY", "")}<br>
                <b>CITY:</b> {row.get("CITY", "")}<br>
                <b>ADDRESS:</b> {row.get("ADDRESS", "")}<br>
                <b>DATE:</b> {row.get("DATE", "")}<br>
                <b>COMMENTS:</b> {row.get("COMMENTS", "")}<br>
                <b>COORDINATES:</b> {lat:.6f}, {lon:.6f}
            </div>
        """

        icon_html = f"""
            <div style="
                background-color: white;
                border: 1px solid #444;
                border-radius: 8px;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.25);
                padding: 4px 10px;
                font-size: 14px;
                font-weight: bold;
                color: #003366;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                text-align: center;
                white-space: nowrap;">
                {row['PROVIDER']}
            </div>
        """

        Marker(
            location=[lat, lon],
            icon=DivIcon(
                icon_size=(150, 36),
                icon_anchor=(75, 18),
                html=icon_html,
            ),
            tooltip=Tooltip(tooltip_html, direction="top", sticky=True),
        ).add_to(cluster)


def df_sqlite(x, y):
    # Paso 1: Cargar los datos desde SQLite usando Polars
    status = st.empty()  # ← Contenedor dinámico de mensajes

    @st.cache_data
    def cargar_datos():
        conn = sqlite3.connect("firmprices.db")
        df = pl.read_database("SELECT * FROM preciosfirmes_ficticios", connection=conn)
        conn.close()

        # Limpieza y formateo con Polars
        df = df.with_columns(
            [
                pl.col("MRC").map_elements(
                    lambda x: f"${x:,.2f}", return_dtype=pl.Utf8
                ),
                pl.col("NRC").map_elements(
                    lambda x: f"${x:,.2f}", return_dtype=pl.Utf8
                ),
                pl.col("BANDWIDTH").map_elements(
                    lambda x: f"{x:,.0f}", return_dtype=pl.Utf8
                ),
                pl.col("TERM").map_elements(
                    lambda x: f"{x:,.0f}", return_dtype=pl.Utf8
                ),
            ]
        )

        # 🔁 CONVERSIÓN FINAL: a pandas para el resto del flujo
        return df.to_pandas()

    # Paso 3: Convertir a Pandas para uso geoespacial
    def convertir_a_geopandas(df: pd.DataFrame) -> geopandas.GeoDataFrame:
        geometry = geopandas.points_from_xy(df["LONGITUDE"], df["LATITUDE"])
        geo_df = geopandas.GeoDataFrame(
            df[
                [
                    "OPPORTUNITY",
                    "COUNTRY",
                    "CITY",
                    "ADDRESS",
                    "LATITUDE",
                    "LONGITUDE",
                    "PROVIDER",
                    "SERVICE",
                    "BANDWIDTH",
                    "TERM",
                    "MRC",
                    "NRC",
                    "DATE",
                    "COMMENTS",
                ]
            ],
            geometry=geometry,
        )
        return geo_df

    # 🚀 Ejecutar flujo completo
    df = cargar_datos()
    status.info("🔍 Cargando datos desde SQLite...")
    time.sleep(0.5)

    status.info("📊 Procesando datos con Polars...")
    time.sleep(0.5)

    status.info("📍 Convirtiendo a GeoDataFrame...")
    time.sleep(0.5)

    geo_df = convertir_a_geopandas(df)

    status.info("🗺️ Construyendo mapa de Folium...")
    time.sleep(0.5)

    # 🗺 Inicializar o reutilizar mapa
    m = folium.Map(
        location=[float(x), float(y)],
        zoom_start=16,
        tiles="OpenStreetMap",
        attr="OpenStreetMap attribution",
    )
    m.location = [float(x), float(y)]
    m.zoom_start = 16

    # Opcional: lista de coordenadas para usar con Folium o similares
    geo_df_list = [[pt.y, pt.x] for pt in geo_df.geometry]

    # Reemplaza 'tu_token_de_acceso' con tu token de acceso de Mapbox
    mapbox_access_token = "YOUR_MAPBOX_TOKEN_HERE"
    # Reemplaza 'tu_estilo_mapbox' con el estilo de Mapbox que desees
    mapbox_style = "satellite-streets-v12"

    # Agregar el Geocoder al mapa
    Geocoder(
        position="topright",
        add_marker_on_click=True,
        placeholder="Find",
        search_button_color="white",
        border_color="black",
        weight=3,
    ).add_to(m)

    # hg = folium.FeatureGroup(name="Services Costs by Provider", show=True).add_to(m)
    cg = folium.FeatureGroup(name="Costs by value (slow to load)", show=False).add_to(m)

    agregar_marcadores_clusterizados(geo_df, m, separacion_metros=30)

    agregar_marcadores_con_estilo(geo_df, cg)

    sg = folium.FeatureGroup(name="Satellite view", show=False).add_to(m)

    mapbox_tiles = folium.TileLayer(
        tiles=f"https://api.mapbox.com/styles/v1/mapbox/{mapbox_style}/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_access_token}",
        attr="Mapbox attribution",
        name="Mapbox",
    ).add_to(sg)

    # Asegurarse de que los popups se muestren siempre

    Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(m)

    m.add_child(folium.LatLngPopup())

    folium.Marker([x, y], popup="Your Site").add_to(m)

    Draw(export=False).add_to(m)

    # Seccion de determinacion de pais
    geolocator = Nominatim(user_agent="MAPAPP")

    # Limitar la frecuencia de peticiones: 1 cada segundo
    reverse = RateLimiter(
        geolocator.reverse, min_delay_seconds=1, max_retries=2, error_wait_seconds=5.0
    )

    # Función de geocodificación inversa segura
    def obtener_direccion_desde_coords(latitud: float, longitud: float):
        try:
            location = reverse(
                (latitud, longitud), language="es"
            )  # Puedes cambiar "es" a otro idioma
            if location and location.address:
                return location.address
            else:
                return "Dirección no encontrada"
        except Exception as e:
            return f"Error: {e}"

    unido = obtener_direccion_desde_coords(x, y)
    address = unido

    der_col, izq_col = st.columns([2, 1])
    with der_col:
        st.write(f"Your address: {address}")

    # === CARGA DE CABLES SUBMARINOS Y TERRESTRES ===

    fg = folium.FeatureGroup(name="Capacity Prices", show=False).add_to(m)

    @st.cache_data
    def cargar_geojson(filepath):
        with open(filepath, "r") as file:
            return json.load(file)

    def reemplazar_nombre(features):
        for feature in features:
            if "name" in feature["properties"]:
                feature["properties"]["name"] = feature["properties"]["name"].replace(
                    "||", "<br>"
                )
        return features

    def obtener_feature(geojson_data, key, value):
        return next(
            (f for f in geojson_data["features"] if f["properties"].get(key) == value),
            None,
        )

    def agregar_cable(geojson_data, cable_id, fg, color="blue", key="id", popup=None):
        feature = obtener_feature(geojson_data, key, cable_id)
        if feature:
            folium.GeoJson(
                feature,
                name="Cable Submarino",
                style_function=lambda x: {
                    "color": x["properties"].get("color", color),
                    "weight": 5,
                    "opacity": 0.8,
                },
                tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Cable Name:"]),
                popup=popup,
            ).add_to(fg)

    # === Procesar cables submarinos ===
    submarine_cables = [
        ("super_1", "blue", "id"),
        ("super_2", "yellow", "feature_id"),
        ("super_3", "yellow", "feature_id"),
    ]

    geojson_sub = cargar_geojson("submarine_demo.geojson")
    geojson_sub["features"] = reemplazar_nombre(geojson_sub["features"])

    for cable_id, color, key in submarine_cables:
        agregar_cable(geojson_sub, cable_id, fg, color, key)

    # === Procesar cables terrestres ===
    terrestres = [
        ("path_geojson_demo.geojson", "Prueba_de_Path", "red", "id", None),
        (
            "path_geojson_2_demo.geojson",
            "Prueba_de_Path_2",
            "red",
            "id",
            folium.GeoJsonPopup(fields=["link"], aliases=["Enlace:"], localize=False),
        ),
        ("path_geojson_3_demo.geojson", "Prueba_de_Path_3", "red", "id", None),
    ]

    for path, cable_id, color, key, popup in terrestres:
        geojson = cargar_geojson(path)
        geojson["features"] = reemplazar_nombre(geojson["features"])
        agregar_cable(geojson, cable_id, fg, color, key, popup)

    folium.LayerControl(collapsed=False).add_to(m)

    # Obtener el HTML del mapa
    map_html = m._repr_html_()

    # Leyenda personalizada
    legend_html = """
    <div style="
        position: absolute;
        bottom: 20px; left: 20px; width: 160px; height: 100px;
        background-color: white; border:2px solid grey; border-radius:6px; padding: 8px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        font-size:12px; font-weight:bold; font-family: Arial; z-index:9999;">
        &nbsp;&nbsp;SERVICES  <br><br>
        <span style="font-size: 16px;">🔵</span> EPL<br>
        <span style="font-size: 16px;">🔴</span> DIA<br>
        <span style="font-size: 16px;">🟢</span> Other services<br>
    </div>
    """

    # Estilo CSS para el input del geocoder
    custom_css = """
    <style>
    .leaflet-control-geocoder-form input {
        color: black !important;
        background-color: #f0f0f0 !important;
    }
    </style>
    """

    # Combinar todo en un solo bloque
    final_html = f"""
    <style>
    .map-container {{
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        width: 100%;
        height: 100%;
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
        {legend_html}
        {custom_css}
    </div>
    """

    status.success("✅ Mapa cargado exitosamente.")
    time.sleep(0.5)
    status.empty()  # Elimina el mensaje de éxito luego de mostrarlo

    # Mostrar en Streamlit
    components.html(final_html, height=1000)

    # Convertir la frase a una lista usando el método split()
    ubicacion = address.split(",")

    country = ubicacion[len(ubicacion) - 1]
    converted_country = unidecode.unidecode(country)
    pais_obtenido = converted_country
    pais_sin_acentos = (
        unicodedata.normalize("NFKD", pais_obtenido)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )
    pais = pais_sin_acentos[1:]

    st.write(pais)


def coordenadas():
    mexico = flag.flag("MX")
    argentina = flag.flag("AR")
    colombia = flag.flag("CO")
    venezuela = flag.flag("VE")
    peru = flag.flag("PE")
    chile = flag.flag("CL")
    rep_dominicana = flag.flag("DO")

    mexico2 = f"{mexico}  CDMX   "
    tijuana = f"{mexico} Tijuana "
    bogota = f"{colombia} Bogota "
    caracas = f"{venezuela}  Caracas "
    lima = f"{peru}  Lima"
    bsas = f"{argentina} BsAs "
    santiago = f"{chile} Santiago "
    santo_domingo = f"{rep_dominicana} Sto. Domingo "

    selected = sac.segmented(
        items=[
            sac.SegmentedItem(label=None),
            sac.SegmentedItem(label=mexico2),
            sac.SegmentedItem(label=tijuana),
            sac.SegmentedItem(label=bogota),
            sac.SegmentedItem(label=caracas),
            sac.SegmentedItem(label=bsas),
            sac.SegmentedItem(label=lima),
            sac.SegmentedItem(label=santiago),
            sac.SegmentedItem(label=santo_domingo),
        ],
        label="""###### Preset Cities""",
        align="left",
        size="xs",
        radius="lg",
        color="gray",
    )

    text_col, button_col = st.columns([2, 1])
    style = """
   <style>
    .css-ocqkz7 {
        position: fixed;
        bottom: 0;
        width: 50%;
        justify-content: center;
        align-items: end;
        margin-bottom: 0.5rem;
       }
   </style>
   """
    # Inject the styling code for both elements
    st.markdown(style, unsafe_allow_html=True)

    with text_col:
        gpsinput_coord = st.text_input(
            "Please enter GPS coordinates:",
            key="gpsinput_coord",
        )

    def obtener_coordenadas_por_seleccion(selected):
        coordenadas_predefinidas = {
            mexico2: ("19.385419124226768", "-99.22714673499631"),
            tijuana: ("32.549803468009", "-117.088738303455"),
            bsas: ("-34.610690192063416", "-58.44600712637896"),
            bogota: ("4.666871383687264", "-74.05256991955729"),
            caracas: ("10.498065761833828", "-66.85179959821086"),
            lima: ("-12.131750880889209", "-77.03053635982998"),
            santiago: ("-33.414489958696805", "-70.60120314756713"),
            santo_domingo: ("18.48233702626038", "-69.9116291547105"),
        }

        return coordenadas_predefinidas.get(selected, (None, None))

    # --- Lógica principal de ejecución optimizada ---
    latitude, longitude = None, None

    if selected is not None:
        latitude, longitude = obtener_coordenadas_por_seleccion(selected)
        if latitude and longitude:
            st.write(f"{selected}: {latitude}, {longitude}")

    # Si el usuario escribió manualmente coordenadas, reemplazamos las anteriores
    coordenadas = gpsinput_coord.split(",")
    if len(coordenadas) == 2:
        latitud_input, longitud_input = coordenadas
        if latitud_input.strip() and longitud_input.strip():
            latitude = latitud_input.strip()
            longitude = longitud_input.strip()

    # Finalmente, solo una llamada a df_sqlite si hay coordenadas válidas
    if latitude and longitude:
        df_sqlite(latitude, longitude)
    else:
        with text_col:
            st.warning("Please enter valid GPS coordinates.")


placeholder = st.empty()


with placeholder.container():

    @st.dialog("\u2003\u2003\u2003\u2003\u2003\u2003\u2003Log In 🔐")
    def login():
        html_atlas = """
        <style>
        @keyframes fadeSlide {
            0% {
                opacity: 0;
                transform: translateY(-20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .logo-anim {
            width: 100%;
            height: 80px;
            font-family: Tahoma, sans-serif;
            font-weight: bold;
            font-size: 36px;
            text-transform: lowercase;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            animation: fadeSlide 1s ease-out;
            /* border-bottom: 1px solid #ccc; */  /* Línea eliminada */
            margin-bottom: 20px;
        }
        .logo-box {
            background-color: white;
            color: black;
            padding: 10px 20px;
            border-radius: 15px;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }
        </style>

        <div class="logo-anim">
            <div class="logo-box">
                atlas.io&nbsp;🌐
            </div>
        </div>
        """
        st.markdown(html_atlas, unsafe_allow_html=True)

        if "submitted" not in st.session_state:
            st.session_state.submitted = False
        if "username" not in st.session_state:
            st.session_state.username = ""

        if not st.session_state.submitted:
            st.session_state.username = st.text_input(
                "Please enter a USER:", value=st.session_state.username
            )
            password = st.text_input("Please enter a Password", type="password")

            if st.button("Submit"):
                user_info = VALID_USERS.get(st.session_state.username)
                if user_info and password == user_info["password"]:
                    email = user_info["email"]
                    code = start_auth_flow(st.session_state.username, password)
                    if code:
                        st.session_state.submitted = True
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas.")
                else:
                    st.error("Usuario o contraseña incorrectos.")
        else:
            code_input = st.text_input("Código de verificación")
            if st.button("Verificar código"):
                if verify_code(code_input):
                    st.success("Verificación exitosa")
                    st.rerun()
                else:
                    st.error("Código incorrecto")


left_co, cent_co, last_co = st.columns(3)


if is_session_active():
    SESSION_DURATION_MINUTES = 25
    elapsed = datetime.now() - session["start_time"]
    remaining = timedelta(minutes=25) - elapsed
    minutes, seconds = divmod(int(remaining.total_seconds()), 60)
    progress = min(elapsed.total_seconds() / 300, 1.0)

    with left_co:
        st.markdown(html_atlas, unsafe_allow_html=True)
        st.markdown(
            "<h3 style='text-align: left; color: white;'>FIRM PRICES TOOL</h3>",
            unsafe_allow_html=True,
        )
    # Notificación JS cuando quede 1 minuto
    start_ms = int(session["start_time"].timestamp() * 1000)
    js = f"""
    <script>
      (function() {{
        const start = {start_ms};
        const duration = 300000; // 5 min
        const now = Date.now();
        const msUntilOneMinLeft = (start + duration - 60000) - now;

        if (msUntilOneMinLeft > 0) {{
          setTimeout(function() {{
            if (Notification.permission !== "granted") {{
              Notification.requestPermission().then(function(p) {{
                if (p === "granted") createNotif();
              }});
            }} else {{
              createNotif();
            }}

            function createNotif() {{
              new Notification("atlas.io", {{
                body: "Queda 1 minuto para cerrar la sesión",
              }});
            }}
          }}, msUntilOneMinLeft);
        }}
      }})();
    </script>
    """
    components.html(js, height=0)

    # Mostrar en sidebar
    with st.sidebar:
        st.success(f"Bienvenido: {session['username']}")
        st.markdown(f"**Tiempo restante:** {minutes} min {seconds} seg")
        st.progress(progress, text=f"{int(progress * 100)}% usado")

        # Botones siempre disponibles en la barra lateral
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reiniciar sesión"):
                now = datetime.now()
                if session.get("start_time"):
                    elapsed = now - session["start_time"]
                    session["total_duration"] += elapsed  # acumula tiempo transcurrido
                session["start_time"] = now  # reinicia el contador
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

    # 🧭 Función principal de la aplicación
    coordenadas()
else:
    login()
