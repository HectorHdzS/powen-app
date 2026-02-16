import streamlit as st
import pandas as pd
import sqlite3

# Configuración de página
st.set_page_config(page_title="Powen Asset Manager", layout="wide", page_icon="☀️")

# --- 1. DICCIONARIO DE GEOLOCALIZACIÓN (32 ESTADOS) ---
# Coordenadas aproximadas del centro de cada estado para el mapa
COORDENADAS = {
    "Aguascalientes": [21.8853, -102.2916],
    "Baja California": [30.8406, -115.2838],
    "Baja California Sur": [26.0444, -111.6661],
    "Campeche": [19.8301, -90.5349],
    "Chiapas": [16.7569, -93.1292],
    "Chihuahua": [28.6330, -106.0691],
    "Ciudad de México": [19.4326, -99.1332],
    "Coahuila de Zaragoza": [27.0587, -101.7068],
    "Colima": [19.2452, -103.7241],
    "Durango": [24.0277, -104.6532],
    "Guanajuato": [21.0190, -101.2574],
    "Guerrero": [17.4392, -99.5451],
    "Hidalgo": [20.0911, -98.7624],
    "Jalisco": [20.6597, -103.3496],
    "Estado de México": [19.3583, -99.6556],
    "Michoacán de Ocampo": [19.5665, -101.7068],
    "Morelos": [18.6813, -99.1013],
    "Nayarit": [21.7514, -104.8455],
    "Nuevo León": [25.6866, -100.3161],
    "Oaxaca": [17.0732, -96.7266],
    "Puebla": [19.0414, -98.2063],
    "Querétaro": [20.5888, -100.3899],
    "Quintana Roo": [19.1817, -88.4791],
    "San Luis Potosí": [22.1565, -100.9855],
    "Sinaloa": [25.1721, -107.4795],
    "Sonora": [29.2972, -110.3309],
    "Tabasco": [17.8409, -92.6189],
    "Tamaulipas": [24.2669, -98.8363],
    "Tlaxcala": [19.3139, -98.2404],
    "Veracruz de Ignacio de la Llave": [19.1738, -96.1342],
    "Yucatán": [20.9674, -89.5926],
    "Zacatecas": [22.7709, -102.5832]
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
        
        # --- AQUÍ ESTÁ EL CAMBIO IMPORTANTE ---
        # Ordenamos la lista alfabéticamente para que sea fácil buscar
        lista_estados = sorted(list(COORDENADAS.keys()))
        ubicacion = col1.selectbox("Ubicación", lista_estados) 
        
        vendedor = col2.text_input("Responsable")
        
        if st.form_submit_button("💾 Guardar Proyecto"):
            if nombre and potencia > 0:
                conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (?,?,?,?)",
                             (nombre, potencia, ubicacion, vendedor))
                conn.commit()
                st.success(f"✅ Proyecto '{nombre}' registrado en {ubicacion}.")
                st.rerun()

# --- SECCIÓN: MAPA ---
elif menu == "🗺️ Mapa de Operaciones":
    st.title("🗺️ Cobertura Nacional")
    
    df_mapa = pd.read_sql_query("SELECT * FROM proyectos", conn)
    
    if not df_mapa.empty:
        # Mapeamos usando el nuevo diccionario completo
        df_mapa['lat'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[0])
        df_mapa['lon'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[1])
        
        datos_mapa = df_mapa.dropna(subset=['lat', 'lon'])
        
        st.map(datos_mapa, latitude='lat', longitude='lon', size=20, color='#FFD700')
        
        with st.expander("Ver detalles de geolocalización"):
            st.dataframe(datos_mapa[['proyecto', 'ubicacion', 'lat', 'lon']])
    else:
        st.warning("No hay datos para mostrar en el mapa.")