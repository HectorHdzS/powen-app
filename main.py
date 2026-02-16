import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Powen Asset Manager", layout="wide")

# 1. Conexión a la Base de Datos SQL
def get_connection():
    return sqlite3.connect("powen_data.db", check_same_thread=False)

# Crear tabla si no existe
conn = get_connection()
conn.execute('''CREATE TABLE IF NOT EXISTS proyectos 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 proyecto TEXT, 
                 potencia REAL, 
                 ubicacion TEXT, 
                 vendedor TEXT)''')
conn.commit()

# 2. Migración única de Excel a SQL
if os.path.exists("PROYECTOS KISHOA.xlsx"):
    # Solo migramos si la tabla de SQL está vacía
    count = conn.execute("SELECT COUNT(*) FROM proyectos").fetchone()[0]
    if count == 0:
        df_excel = pd.read_excel("PROYECTOS KISHOA.xlsx", header=1)
        df_excel.columns = df_excel.columns.str.strip()
        # Mapeamos columnas (asegúrate que los nombres coincidan con tu Excel)
        df_sql = df_excel[['PROYECTO', 'POTENCIA', 'UBICACIÓN']].copy()
        df_sql.columns = ['proyecto', 'potencia', 'ubicacion']
        df_sql['vendedor'] = "Migración"
        df_sql.to_sql('proyectos', conn, if_exists='append', index=False)
        st.success("✅ Datos migrados de Excel a SQL exitosamente.")

# 3. Interfaz de la Aplicación
st.title("☀️ Powen - Control de Proyectos Fotovoltaicos")

# Formulario para ingresar información nueva
with st.expander("➕ Registrar Nuevo Proyecto"):
    with st.form("registro"):
        col_a, col_b = st.columns(2)
        nombre = col_a.text_input("Nombre del Proyecto")
        pot = col_b.number_input("Capacidad (kW)", min_value=0.0)
        ubi = col_a.selectbox("Estado", ["Aguascalientes", "CDMX", "Jalisco", "Querétaro", "Edomex"])
        vend = col_b.text_input("Vendedor asignado")
        
        if st.form_submit_button("Guardar en Base de Datos"):
            if nombre and pot > 0:
                conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (?,?,?,?)",
                             (nombre, pot, ubi, vend))
                conn.commit()
                st.success(f"¡Proyecto {nombre} guardado!")
                st.rerun()
            else:
                st.warning("Por favor llena el nombre y la potencia.")

# 4. Visualización de Datos
df_final = pd.read_sql_query("SELECT * FROM proyectos ORDER BY id DESC", conn)
st.subheader("Base de Datos Consolidada")
st.dataframe(df_final, use_container_width=True)

st.metric("Potencia Total Instalada (SQL)", f"{df_final['potencia'].sum():,.2f} kW")