import sqlite3

import geopandas
import matplotlib.pyplot as plt
import pandas as pd

# ==============================
# atlas.io Version 1.2.0 - Copyright © White Labs Technologies 2025
# author: Jhonattan W. Blanco
# ==============================

# ARCHIVO PARA CREAR Y CARGA

# Leer el archivo Excel
excel_file = "FIRM PRICES 2024.xlsx"
df = pd.read_excel(excel_file, sheet_name="Sheet1")


# Crear la base de datos SQLite
def create_db():
    conn = sqlite3.connect("firmprices.db")
    conn.commit()
    conn.close()
    print("Database created successfully")


# Crear la tabla
def create_table():
    conn = sqlite3.connect("firmprices.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS preciosfirmes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        OPPORTUNITY text,
        COUNTRY text,
        CITY text,
        ADDRESS text,
        LATITUDE real,
        LONGITUDE real,
        PROVIDER text,
        SERVICE text,
        BANDWIDTH real,
        TERM real,
        MRC real,
        NRC real,
        DATE text,
        COMMENTS text
    )"""
    )
    print("Table created successfully")
    conn.commit()
    conn.close()


# Insertar los datos en la tabla
def insert_data():
    conn = sqlite3.connect("firmprices.db")
    c = conn.cursor()
    for index, row in df.iterrows():
        OPPORTUNITY = row["OPPORTUNITY"]
        COUNTRY = row["COUNTRY"]
        CITY = row["CITY"]
        ADDRESS = row["ADDRESS"]
        LATITUDE = row["LATITUDE"]
        LONGITUDE = row["LONGITUDE"]
        PROVIDER = row["PROVIDER"]
        SERVICE = row["SERVICE"]
        BANDWIDTH = row["BANDWIDTH"]
        TERM = row["TERM"]
        MRC = row["MRC"]
        NRC = row["NRC"]
        DATE = row["DATE"]
        COMMENTS = row["COMMENTS"]
        c.execute(
            """INSERT INTO preciosfirmes (OPPORTUNITY,
                COUNTRY,
                CITY,
                ADDRESS,
                LATITUDE,
                LONGITUDE,
                PROVIDER,
                SERVICE,
                BANDWIDTH,
                TERM,
                MRC,
                NRC,
                DATE,
                COMMENTS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ? );""",
            (
                OPPORTUNITY,
                COUNTRY,
                CITY,
                ADDRESS,
                LATITUDE,
                LONGITUDE,
                PROVIDER,
                SERVICE,
                BANDWIDTH,
                TERM,
                MRC,
                NRC,
                DATE,
                COMMENTS,
            ),
        )

    # Guardar los cambios
    conn.commit()
    # Cerrar la conexión
    conn.close()
    print("Data inserted successfully")


def dataframe_sqlite():
    conn = sqlite3.connect("firmprices.db")
    c = conn.cursor()
    c.execute("SELECT * FROM preciosfirmes ORDER BY ID")
    datos = c.fetchall()
    dataframe = pd.DataFrame(datos, columns=[i[0] for i in c.description])

    conn.close()
    print(dataframe)


def df_sqlite():
    conn = sqlite3.connect("firmprices.db")
    df = pd.read_sql_query("SELECT * from preciosfirmes", conn)

    # Verify that result of SQL query is stored in the dataframe
    # print(df.head())

    # df1 = df.loc[:, ("LATITUDE", "LONGITUDE")]

    # print(df1.head())

    # Create point geometries
    geometry = geopandas.points_from_xy(df.LONGITUDE, df.LATITUDE)
    geo_df = geopandas.GeoDataFrame(
        df[["COUNTRY", "CITY", "ADDRESS", "LATITUDE", "LONGITUDE"]], geometry=geometry
    )

    print(geo_df)  # geo_df.head()

    conn.close()


def df_delete():
    conn = sqlite3.connect("firmprices.db")
    c = conn.cursor()
    c.execute("DELETE FROM preciosfirmes")
    conn.commit()
    conn.close()
    print("Data deleted successfully")


if __name__ == "__main__":
    # create_db()
    # create_table()
    insert_data()
    # dataframe_sqlite()
    # df_sqlite()
