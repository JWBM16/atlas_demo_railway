import os
import sqlite3
import pandas as pd
import streamlit as st
import streamlit_space

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
        "<h3 style='text-align: left; color: white;'>PRICE LIST (Updated 2025-jun-04)</h3>",
        unsafe_allow_html=True,
    )

conn = sqlite3.connect("listadeprecios.db")
df = pd.read_sql_query("SELECT * from listaprecios", conn)

df_filtered = pd.DataFrame()

provider = None

country_options = df["COUNTRY"].unique()
country_options = pd.Series(country_options)
country_options = country_options.sort_values()

country_select = st.multiselect("Select Country", country_options, key="country")

country_select_changed = False

col1, col2 = st.columns(2)
if country_select:
    country_select_changed = True
    df_filtered = df[df["COUNTRY"].isin(country_select)]

    with col1:
        service_options = df_filtered["SERVICE"].unique()
        service_options = pd.Series(service_options)
        service_options = service_options.sort_values()

        service_select = st.multiselect(
            "Select Service", service_options, key="service"
        )

        provider_options = df_filtered["PROVIDER"].unique()
        provider_options = pd.Series(provider_options)
        provider_options = provider_options.sort_values()

        provider_select = st.multiselect(
            "Select Provider", provider_options, key="provider"
        )
    with col2:
        bandwidth_options = df_filtered["BANDWIDTH"].unique()
        bandwidth_options = pd.Series(bandwidth_options)
        bandwidth_options = bandwidth_options.sort_values()

        bandwidth_select = st.multiselect(
            "Select Bandwidth", bandwidth_options, key="bandwidth"
        )

        term_options = df_filtered["TERM"].unique()
        term_options = pd.Series(term_options)
        term_options = term_options.sort_values()

        term_select = st.multiselect("Select Term", term_options, key="term")

    if (
        service_select
        and provider_select
        and bandwidth_select
        and term_select
        and country_select_changed
    ):
        df_filtered_dos = df_filtered[
            (df_filtered["SERVICE"].isin(service_select))
            & (df_filtered["PROVIDER"].isin(provider_select))
            & (df_filtered["BANDWIDTH"].isin(bandwidth_select))
            & (df_filtered["TERM"].isin(term_select))
        ]
        df_filtered_dos = df_filtered_dos.drop(["ID"], axis=1)
        df_filtered_dos = df_filtered_dos.set_index("COUNTRY")
        if not df_filtered.empty:
            streamlit_space.space(container=None, lines=1)
            st.write(df_filtered_dos)

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
