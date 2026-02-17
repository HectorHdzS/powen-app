import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- CONFIGURACIÓN DE PÁGINA Y LOGO ---
st.set_page_config(page_title="POWEN INDUSTRIAL", layout="wide", page_icon="🏭")

# Logo oficial
st.logo("logo.png")

# --- 1. DICCIONARIO DE GEOLOCALIZACIÓN ---
COORDENADAS = {
    "Aguascalientes": [21.8853, -102.2916], "Baja California": [30.8406, -115.2838],
    "Baja California Sur": [26.0444, -111.6661], "Campeche": [19.8301, -90.5349],
    "Chiapas": [16.7569, -93.1292], "Chihuahua": [28.6330, -106.0691],
    "Ciudad de México": [19.4326, -99.1332], "Coahuila": [27.0587, -101.7068],
    "Colima": [19.2452, -103.7241], "Durango": [24.0277, -104.6532],
    "Guanajuato": [21.0190, -101.2574], "Guerrero": [17.4392, -99.5451],
    "Hidalgo": [20.0911, -98.7624], "Jalisco": [20.6597, -103.3496],
    "Estado de México": [19.3583, -99.6556], "Michoacán": [19.5665, -101.7068],
    "Morelos": [18.6813, -99.1013], "Nayarit": [21.7514, -104.8455],
    "Nuevo León": [25.6866, -100.3161], "Oaxaca": [17.0732, -96.7266],
    "Puebla": [19.0414, -98.2063], "Querétaro": [20.5888, -100.3899],
    "Quintana Roo": [19.1817, -88.4791], "San Luis Potosí": [22.1565, -100.9855],
    "Sinaloa": [25.1721, -107.4795], "Sonora": [29.2972, -110.3309],
    "Tabasco": [17.8409, -92.6189], "Tamaulipas": [24.2669, -98.8363],
    "Tlaxcala": [19.3139, -98.2404], "Veracruz": [19.1738, -96.1342],
    "Yucatán": [20.9674, -89.5926], "Zacatecas": [22.7709, -102.5832]
}

# --- 2. CONEXIÓN A LA NUBE (NEON / POSTGRESQL) ---
def get_engine():
    return st.connection("postgresql", type="sql")

conn = get_engine()

# Crear tabla si no existe
with conn.session as s:
    s.execute(text('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id SERIAL PRIMARY KEY,
            proyecto TEXT, potencia REAL, ubicacion TEXT, vendedor TEXT
        );
    '''))
    s.commit()

# --- 3. MENÚ LATERAL ---
# Agregamos las nuevas pestañas a la lista
menu = st.sidebar.radio(
    "MENÚ PRINCIPAL", 
    ["📊 Dashboard", "➕ Registro de Proyectos", "🗺️ Mapa de Operaciones", "🏗️ Operaciones B2B", "🔧 O&M"]
)

# --- SECCIÓN: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("🏭 POWEN INDUSTRIAL")
    st.markdown("**Dashboard Proyectos B2B**")
    
    df = conn.query("SELECT * FROM proyectos", ttl=0)
    
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Proyectos Activos", len(df))
        c2.metric("Potencia Total", f"{df['potencia'].sum():,.2f} kW")
        c3.metric("Cobertura Estatal", df['ubicacion'].nunique())
        
        st.divider()
        
        col_graf, col_tabla = st.columns([1, 2])
        
        col_graf.subheader("Potencia por Estado")
        col_graf.bar_chart(df.groupby("ubicacion")["potencia"].sum(), color="#FFD700")
        
        col_tabla.subheader("Detalle de Proyectos")
        col_tabla.dataframe(df, use_container_width=True)
    else:
        st.info("La base de datos en la nube está vacía. ¡Ve a la pestaña de registro!")

# --- SECCIÓN: REGISTRO ---
elif menu == "➕ Registro de Proyectos":
    st.title("➕ Alta de Nuevos Proyectos")
    st.markdown("Ingresa los datos del nuevo contrato industrial.")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del Proyecto / Cliente")
        potencia = col2.number_input("Capacidad Fotovoltaica (kW)", min_value=0.0)
        ubicacion = col1.selectbox("Ubicación del Sitio", sorted(list(COORDENADAS.keys())))
        vendedor = col2.text_input("Project Manager Responsable")
        
        if st.form_submit_button("💾 Guardar en Nube"):
            if nombre and potencia > 0:
                with conn.session as s:
                    s.execute(
                        text("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (:p, :kw, :u, :v)"),
                        params={"p": nombre, "kw": potencia, "u": ubicacion, "v": vendedor}
                    )
                    s.commit()
                st.success(f"✅ Proyecto '{nombre}' guardado exitosamente en Neon.")
                st.rerun()
            else:
                st.error("Por favor ingresa al menos el nombre y una potencia mayor a 0.")

# --- SECCIÓN: MAPA ---
elif menu == "🗺️ Mapa de Operaciones":
    st.title("🗺️ Cobertura Nacional")
    
    df_mapa = conn.query("SELECT * FROM proyectos", ttl=0)
    
    if not df_mapa.empty:
        df_mapa['lat'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[0])
        df_mapa['lon'] = df_mapa['ubicacion'].map(lambda x: COORDENADAS.get(x, [None, None])[1])
        
        datos_mapa = df_mapa.dropna(subset=['lat', 'lon'])
        
        st.map(datos_mapa, latitude='lat', longitude='lon', size=20, color='#FFD700')
        st.dataframe(datos_mapa[['proyecto', 'ubicacion', 'potencia']], use_container_width=True)
    else:
        st.warning("No hay proyectos registrados para mostrar en el mapa.")

# --- NUEVA SECCIÓN: OPERACIONES B2B ---
elif menu == "🏗️ Operaciones B2B":
    st.title("🏗️ Gestión de Obra e Ingeniería")
    st.info("🚧 Módulo en construcción. Aquí gestionaremos el avance de obra, cronogramas y asignación de instaladores.")

# --- NUEVA SECCIÓN: O&M ---
elif menu == "🔧 O&M":
    st.title("🔧 Operación y Mantenimiento")
    st.info("🚧 Módulo en construcción. Aquí se visualizarán tickets de servicio, monitoreo en tiempo real y limpiezas programadas.")