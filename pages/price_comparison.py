import math
import os
import sqlite3
import pandas as pd
import streamlit as st
import streamlit_shadcn_ui as ui
import streamlit_space

from streamlit_space import space
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


cols = st.columns(3)
with cols[0]:
    st.markdown(html_atlas, unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align: left; color: white;'>PRICE COMPARISON</h3>",
        unsafe_allow_html=True,
    )


with cols[1]:
    streamlit_space.space(container=None, lines=3)

country_to_find = st.text_input(
    "Please enter the country to search:",
    key="countfind",
)


conn = sqlite3.connect("firmprices.db")
df_pf = pd.read_sql_query("SELECT * from preciosfirmes", conn)

# ----SECCION LISTA DE PRECIOS ----- #
# conexion con la DB firmprices.db
conn = sqlite3.connect("listadeprecios.db")
df_lp = pd.read_sql_query("SELECT * from listaprecios", conn)


def busqueda(country):
    if country != "":
        country_short = country[:-2]
        resultados = df_pf[df_pf["COUNTRY"].str.contains(country_short, case=False)]
        resultados_lp = df_lp[df_lp["COUNTRY"].str.contains(country_short, case=False)]

        with cols[0]:
            # Listado de proveedores como Opciones
            proveedor_options = resultados["PROVIDER"].unique()
            proveedor_options = pd.Series(proveedor_options)
            proveedor_options = proveedor_options.sort_values()
            provider_select = st.selectbox(
                "Select Provider", proveedor_options, key="provider"
            )
        # Listado de proveedores como Opciones
        with cols[1]:
            bandwidth_options = resultados["BANDWIDTH"].unique()
            bandwidth_options = pd.Series(bandwidth_options)
            bandwidth_options = bandwidth_options.sort_values()

            streamlit_space.space(container=None, lines=2)
            st.markdown("######")
            bandwidth_select = st.selectbox(
                "Select Bandwidth", bandwidth_options, key="bandwidth"
            )
        provider_to_find_changed = False
        bandwidth_to_find_changed = False

        if provider_select and bandwidth_select:
            resultados_filtered = resultados[
                (resultados["PROVIDER"].isin([provider_select]))
                & (resultados["BANDWIDTH"].isin([bandwidth_select]))
            ]
            resultados_filtered = resultados_filtered.drop(["ID"], axis=1)

            # filtrado a 12 meses
            average_doce = resultados_filtered[resultados_filtered["TERM"] == 12]
            average_doce_mrc = average_doce["MRC"].mean()

            # filtrado 36 meses
            average_treintaseis = resultados_filtered[resultados_filtered["TERM"] == 36]
            average_treintaseis_mrc = average_treintaseis["MRC"].mean()

            resultados_lp_uno = resultados_lp[
                resultados_lp["PROVIDER"].str.contains(provider_select[0], case=False)
            ]

            resultados_lp_dos = resultados_lp_uno[
                (resultados_lp_uno["BANDWIDTH"].isin([bandwidth_select]))
            ]

            # filtrado a 12 meses
            resultados_lp_doce = resultados_lp_dos[resultados_lp_dos["TERM"] == 12]
            resultado_lp_doce_dos = resultados_lp_doce[
                resultados_lp_doce["SERVICE"] == "L2"
            ]
            average_lp_doce_mrc = resultado_lp_doce_dos["MRC"].mean()

            # filtrado a 36 meses
            resultados_lp_treintaseis = resultados_lp_dos[
                resultados_lp_dos["TERM"] == 36
            ]
            resultado_lp_treintaseis_dos = resultados_lp_treintaseis[
                resultados_lp_treintaseis["SERVICE"] == "L2"
            ]

            # PRUEBA DE DATAFRAME
            df_filtered_dos = resultados_lp[
                (resultados_lp["PROVIDER"].isin([provider_select]))
                & (resultados_lp["BANDWIDTH"].isin([bandwidth_select]))
            ]

            average_lp_treintaseis_mrc = resultado_lp_treintaseis_dos["MRC"].mean()

            para_doce = (average_doce_mrc / average_lp_doce_mrc) - 1
            para_treintaseis = (
                average_treintaseis_mrc / average_lp_treintaseis_mrc
            ) - 1

            if para_doce < 0:
                texto_doce = "12 Months Firm MRC is cheaper 💰 than MRC Price List"
                para_doce = para_doce * -1
            else:
                texto_doce = "12 Months Firm MRC is more expensive than MRC Price List"

            if para_treintaseis < 0:
                texto_treintaseis = "36 Months Firm MRC is cheaper than MRC Price List"
                para_treintaseis = para_treintaseis * -1
            else:
                texto_treintaseis = (
                    "36 Months Firm MRC is more expensive than MRC Price List"
                )

            # CALCULOS DE DIFERENCIA ENTRE FIRME
            if not math.isnan(para_doce) and not math.isnan(para_treintaseis):
                if math.isnan(average_doce_mrc):
                    contenido = "NO DATA"
                else:
                    contenido = f"${average_doce_mrc:,.2f}"
                if math.isnan(average_treintaseis_mrc):
                    contenido_treintaseis = "NO DATA"
                else:
                    contenido_treintaseis = f"${average_treintaseis_mrc:,.2f}"
                with cols[0]:
                    ui.metric_card(
                        title="12 Months Firm MRC avg. for the BW and Provider",
                        content=contenido,
                        description=f"{texto_doce} in {para_doce:.2%}",
                        key="card1",
                    )
                with cols[1]:
                    ui.metric_card(
                        title="36 Months Firm MRC avg. for the BW and Provider",
                        content=contenido_treintaseis,
                        description=f"{texto_treintaseis} in {para_treintaseis:.2%}",
                        key="card2",
                    )
                proveedor_short = provider_select
                st.write(
                    f" ### Firm Prices for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(resultados_filtered)
                st.write(
                    f" 📃 Price List for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(df_filtered_dos)

            elif math.isnan(para_doce) and not math.isnan(para_treintaseis):
                if math.isnan(average_doce_mrc):
                    contenido = "NO DATA"
                else:
                    contenido = f"${average_doce_mrc:,.2f}"
                if math.isnan(average_treintaseis_mrc):
                    contenido_treintaseis = "NO DATA"
                else:
                    contenido_treintaseis = f"${average_treintaseis_mrc:,.2f}"
                with cols[0]:
                    ui.metric_card(
                        title="12 Months Firm MRC avg. for the BW and Provider",
                        content=contenido,
                        description="There is not data in firm prices for this Bandwidth and Provider",
                        key="card3",
                    )
                with cols[1]:
                    ui.metric_card(
                        title="36 Months Firm MRC avg. for the BW and Provider",
                        content=contenido_treintaseis,
                        description=f"{texto_treintaseis} in {para_treintaseis:.2%}",
                        key="card4",
                    )
                st.write(
                    "Provider's MRC cannot be compared with Price List in 12 Months values."
                )
                proveedor_short = provider_select
                st.write(
                    f"Firm Prices for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(resultados_filtered)
                st.write(
                    f" 📃 Price List for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                # st.write(resultados_lp_dos)
                st.write(df_filtered_dos)

            elif not math.isnan(para_doce) and math.isnan(para_treintaseis):
                if math.isnan(average_doce_mrc):
                    contenido = "NO DATA"
                else:
                    contenido = f"${average_doce_mrc:,.2f}"
                if math.isnan(average_treintaseis_mrc):
                    contenido_treintaseis = "NO DATA"
                else:
                    contenido_treintaseis = f"${average_treintaseis_mrc:,.2f}"
                with cols[0]:
                    ui.metric_card(
                        title="12 Months Firm MRC avg. for the BW and Provider",
                        content=contenido,
                        description=f"{texto_doce} in {para_doce:.2%}",
                        key="card5",
                    )
                with cols[1]:
                    ui.metric_card(
                        title="36 Months Firm MRC avg. for the BW and Provider",
                        content=contenido_treintaseis,
                        description="There is no data in the price list to be compared for this Bandwidth and Provider",
                        key="card6",
                    )
                proveedor_short = provider_select
                st.write(
                    f"Firm Prices for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(resultados_filtered)
                st.write(
                    f" 📃 Price List for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(df_filtered_dos)

            elif math.isnan(para_doce) and math.isnan(para_treintaseis):
                if math.isnan(average_doce_mrc):
                    contenido = "NO DATA"
                else:
                    contenido = f"${average_doce_mrc:,.2f}"
                if math.isnan(average_treintaseis_mrc):
                    contenido_treintaseis = "NO DATA"
                else:
                    contenido_treintaseis = f"${average_treintaseis_mrc:,.2f}"
                with cols[0]:
                    ui.metric_card(
                        title="12 Months Firm MRC avg. for the BW and Provider",
                        content=contenido,
                        description="There is no data in the price list for this Bandwidth and Provider",
                        key="card7",
                    )
                with cols[1]:
                    ui.metric_card(
                        title="36 Months Firm MRC avg. for the BW and Provider",
                        content=contenido_treintaseis,
                        description="There is no data in the price list for this Bandwidth and Provider",
                        key="card8",
                    )
                proveedor_short = provider_select
                st.write(
                    f"Firm Prices for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(resultados_filtered)
                st.write(
                    f" 📃 Price List for: {proveedor_short} and Bandwidth: {bandwidth_select}"
                )
                st.write(df_filtered_dos)


if len(country_to_find) > 0:
    country_busqueda = rf"{country_to_find}.*"
    busqueda(country_busqueda)

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
