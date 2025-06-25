import sqlite3

import pandas as pd

# Leer el archivo Excel
excel_file = "price_list.xlsx"
df = pd.read_excel(excel_file, sheet_name="Sheet1")


# Crear la base de datos SQLite
def create_db():
    conn = sqlite3.connect("listadeprecios.db")
    conn.commit()
    conn.close()
    print("Database created successfully")


# Crear la tabla
def create_table():
    conn = sqlite3.connect("listadeprecios.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS listaprecios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        COUNTRY text,
        PROVIDER text,
        BANDWIDTH real,
        SERVICE text,
        TECHNOLOGY text,
        TERM real,
        MRC real,
        NRC real,
        COMMENTS text
    )"""
    )
    print("Table created successfully")
    conn.commit()
    conn.close()


# Insertar los datos en la tabla
def insert_data():
    conn = sqlite3.connect("listadeprecios.db")
    c = conn.cursor()
    for index, row in df.iterrows():
        COUNTRY = row["COUNTRY"]
        PROVIDER = row["PROVIDER"]
        BANDWIDTH = row["BANDWIDTH"]
        SERVICE = row["SERVICE"]
        TECHNOLOGY = row["TECHNOLOGY"]
        TERM = row["TERM"]
        MRC = row["MRC"]
        NRC = row["NRC"]
        COMMENTS = row["COMMENTS"]
        c.execute(
            """INSERT INTO listaprecios (COUNTRY, PROVIDER, BANDWIDTH, SERVICE, TECHNOLOGY, TERM, MRC, NRC, COMMENTS) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                COUNTRY,
                PROVIDER,
                BANDWIDTH,
                SERVICE,
                TECHNOLOGY,
                TERM,
                MRC,
                NRC,
                COMMENTS,
            ),
        )

    # Guardar los cambios
    conn.commit()
    # Cerrar la conexión
    conn.close()
    print("Data inserted successfully")


def dataframe_sqlite():
    conn = sqlite3.connect("listadeprecios.db")
    c = conn.cursor()
    c.execute("SELECT * FROM listaprecios ORDER BY ID")
    datos = c.fetchall()
    dataframe = pd.DataFrame(datos, columns=[i[0] for i in c.description])

    conn.close()
    print(dataframe)


# def df_sqlite():
#     conn = sqlite3.connect("listadeprecios.db")
#     df = pd.read_sql_query("SELECT * from listaprecios", conn)

#     # Verify that result of SQL query is stored in the dataframe
#     print(df.head())

#     conn.close()


def df_delete():
    conn = sqlite3.connect("firmprices.db")
    c = conn.cursor()
    c.execute("DELETE FROM preciosfirmes")
    conn.commit()
    conn.close()


def clear_table_and_reset_id():
    conn = sqlite3.connect("listadeprecios.db")
    c = conn.cursor()
    c.execute("DELETE FROM listaprecios")
    c.execute("DELETE FROM sqlite_sequence WHERE name='listaprecios'")
    conn.commit()
    conn.close()
    print("Table cleared and ID reset")


if __name__ == "__main__":
    # create_db()
    # create_table()
    insert_data()
    # dataframe_sqlite()
    # df_delete()
    # df_sqlite()
    # clear_table_and_reset_id()
