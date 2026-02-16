import streamlit as st
import pandas as pd
import sqlite3

# Configuración de página
st.set_page_config(page_title="Powen Asset Manager", layout="wide", page_icon="☀️")

# --- 1. DICCIONARIO DE GEOLOCALIZACIÓN ---
# Aquí "traducimos" los nombres de los estados a coordenadas (Latitud, Longitud)
COORDENADAS = {
    "CDMX": [19.4326, -99.1332],
    "Edomex": [19.3583, -99.6556],
    "Nuevo León": [25.6866, -100.3161],
    "Jalisco": [20.6597, -103.3496],
    "Querétaro": [20.5888, -100.3899],
    "Yucatán": [20.9674, -89.5926],
    "Puebla": [19.0414, -98.2063],
    "Aguascalientes": [21.8853, -102.2916],
    "Guanajuato": [21.0190, -101.2574],
    "Veracruz": [19.1738, -96.1342]
}

# --- 2. CONEXIÓN BASE DE DATOS ---
def get_connection():
    return sqlite3.connect("powen_data.db", check_same_thread=False)

conn = get_connection()
conn.execute('''
    CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto TEXT, potencia REAL, ubicacion TEXT, vendedor TEXT
    )
''')
conn.commit()

# --- 3. MENÚ LATERAL ---
try:
    st.sidebar.image("https://powen.mx/wp-content/uploads/2023/05/Logo-Powen-Negro.png", width=150)
except:
    st.sidebar.header("POWEN")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["📊 Dashboard", "➕ Registro de Proyectos", "🗺️ Mapa de Operaciones"])

# --- SECCIÓN: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Panel de Control Fotovoltaico")
    df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Proyectos Totales", len(df))
        c2.metric("Potencia Instalada", f"{df['potencia'].sum():,.2f} kW")
        c3.metric("Cobertura (Estados)", df['ubicacion'].nunique())
        st.divider()
        col_graf, col_tabla = st.columns([1, 2])
        col_graf.bar_chart(df.groupby("ubicacion")["potencia"].sum(), color="#FFD700")
        col_tabla.dataframe(df, use_container_width=True)
    else:
        st.info("Base de datos vacía. Registra tu primer proyecto.")

# --- SECCIÓN: REGISTRO ---
elif menu == "➕ Registro de Proyectos":
    st.title("➕ Alta de Nuevos Proyectos")
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del Proyecto")
        potencia = col2.number_input("Capacidad (kW)", min_value=0.0)
        # Usamos las llaves del diccionario para asegurar que el mapa funcione
        ubicacion = col1.selectbox("Ubicación", list(COORDENADAS.keys())) 
        vendedor = col2.text_input("Responsable")
        
        if st.form_submit_button("💾 Guardar Proyecto"):
            if nombre and potencia > 0:
                conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (?,?,?,?)",
                             (nombre, potencia, ubicacion, vendedor))
                conn.commit()
                st.success(f"✅ Proyecto '{nombre}' registrado en {ubicacion}.")
                st.rerun()

# --- SECCIÓN: MAPA (NUEVO) ---
elif menu == "🗺️ Mapa de Operaciones":
    st.title("🗺️ Cobertura Nacional")
    
    df_mapa = pd.read_sql_query("SELECT * FROM proyectos", conn)
    
    if not df_mapa.empty:
        # Aquí ocurre la magia: Agregamos latitud y longitud buscando en el diccionario
        df_mapa['lat'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[0])
        df_mapa['lon'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[1])
        
        # Filtramos errores (por si hay un estado viejo que no tenga coordenadas)
        datos_mapa = df_mapa.dropna(subset=['lat', 'lon'])
        
        # Mostramos el mapa
        st.map(datos_mapa, latitude='lat', longitude='lon', size=20, color='#FFD700')
        
        with st.expander("Ver detalles de geolocalización"):
            st.dataframe(datos_mapa[['proyecto', 'ubicacion', 'lat', 'lon']])
    else:
        st.warning("No hay datos para mostrar en el mapa.")