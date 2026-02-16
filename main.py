import streamlit as st
import pandas as pd
import sqlite3

# Configuración profesional de la página
st.set_page_config(page_title="Powen Asset Manager", layout="wide", page_icon="☀️")

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    return sqlite3.connect("powen_data.db", check_same_thread=False)

conn = get_connection()

# --- NAVEGACIÓN LATERAL ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/50/Closed_Access_logo_transparent.png", width=100) # Puedes poner el logo de Powen aquí
menu = st.sidebar.radio("MENÚ PRINCIPAL", ["📊 Dashboard", "➕ Registro de Proyectos", "🗺️ Mapa de Operaciones"])

# --- SECCIÓN 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Panel de Control Fotovoltaico")
    df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    
    if not df.empty:
        # Métricas principales
        c1, c2, c3 = st.columns(3)
        c1.metric("Proyectos Totales", len(df))
        c2.metric("Potencia Instalada", f"{df['potencia'].sum():,.2f} kW")
        c3.metric("Ubicaciones", df['ubicacion'].nunique())
        
        st.divider()
        
        # Gráfica de potencia por proyecto
        st.subheader("Capacidad por Proyecto")
        st.bar_chart(data=df, x="proyecto", y="potencia", color="#FFD700")
        
        st.subheader("Listado Maestro")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay datos. Dirígete a 'Registro de Proyectos' para añadir el primero.")

# --- SECCIÓN 2: REGISTRO ---
elif menu == "➕ Registro de Proyectos":
    st.title("➕ Alta de Nuevos Proyectos")
    st.write("Ingresa los detalles técnicos para actualizar la base de datos de Powen.")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del Proyecto (Cliente/Sitio)")
        potencia = col2.number_input("Capacidad Instalada (kW)", min_value=0.0, step=0.1)
        ubicacion = col1.selectbox("Estado de la República", ["CDMX", "Edomex", "Querétaro", "Jalisco", "Nuevo León", "Yucatán"])
        vendedor = col2.text_input("Ingeniero / Vendedor Responsable")
        
        submitted = st.form_submit_button("Confirmar Registro")
        
        if submitted:
            if nombre and potencia > 0:
                conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (?,?,?,?)",
                             (nombre, potencia, ubicacion, vendedor))
                conn.commit()
                st.success(f"✅ Proyecto '{nombre}' guardado exitosamente en SQL.")
            else:
                st.error("Por favor completa los campos obligatorios (Nombre y Potencia).")

# --- SECCIÓN 3: MAPA ---
elif menu == "🗺️ Mapa de Operaciones":
    st.title("🗺️ Cobertura Nacional")
    st.info("Próximamente: Integración de coordenadas GPS para visualizar cada planta fotovoltaica.")
    # Aquí es donde en el futuro usaremos una tabla de latitudes y longitudes