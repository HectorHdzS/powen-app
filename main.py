import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Powen Asset Manager", layout="wide")
st.title("☀️ Powen - Control de Proyectos")

# 1. Conectar a SQL
conn = sqlite3.connect("powen_data.db", check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS proyectos 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 proyecto TEXT, potencia REAL, ubicacion TEXT, vendedor TEXT)''')
conn.commit()

# 2. Migración "Inteligente"
if os.path.exists("PROYECTOS KISHOA.xlsx"):
    count = conn.execute("SELECT COUNT(*) FROM proyectos").fetchone()[0]
    if count == 0:
        try:
            # Probamos leer el Excel saltando filas hasta encontrar los títulos
            # Si el error persiste, cambia 'header=1' por 'header=2'
            df_excel = pd.read_excel("PROYECTOS KISHOA.xlsx", header=1)
            
            # Limpiamos los nombres de las columnas detectadas
            df_excel.columns = df_excel.columns.astype(str).str.strip().str.upper()
            
            # Buscamos las columnas reales aunque tengan otros nombres
            # Mapeo: {Nombre en Excel : Nombre en SQL}
            columnas = {'PROYECTO': 'proyecto', 'POTENCIA': 'potencia', 'UBICACIÓN': 'ubicacion'}
            
            # Solo filtramos las que existan
            cols_encontradas = [c for c in columnas.keys() if c in df_excel.columns]
            
            if len(cols_encontradas) > 0:
                df_migrar = df_excel[cols_encontradas].copy()
                df_migrar.rename(columns=columnas, inplace=True)
                df_migrar['vendedor'] = "Carga Inicial"
                df_migrar.to_sql('proyectos', conn, if_exists='append', index=False)
                st.success("✅ Datos migrados correctamente a SQL.")
            else:
                st.error(f"No encontré las columnas. Columnas en el Excel: {list(df_excel.columns)}")
        except Exception as e:
            st.error(f"Error al leer Excel: {e}")

# 3. Formulario de Captura
with st.expander("➕ Registrar Nuevo Proyecto"):
    with st.form("nuevo"):
        p_nom = st.text_input("Nombre del Proyecto")
        p_pot = st.number_input("Potencia (kW)", min_value=0.0)
        p_ubi = st.text_input("Ubicación")
        if st.form_submit_button("Guardar"):
            conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion) VALUES (?,?,?)", (p_nom, p_pot, p_ubi))
            conn.commit()
            st.rerun()

# 4. Mostrar Datos desde SQL (No más Excel)
df_final = pd.read_sql_query("SELECT * FROM proyectos", conn)
st.dataframe(df_final, use_container_width=True)