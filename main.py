import streamlit as st
import pandas as pd
import sqlite3

# Configuración de la página
st.set_page_config(page_title="Powen Asset Manager", layout="wide", page_icon="☀️")

# --- CONEXIÓN A BASE DE DATOS ---
def get_connection():
    # Conectamos a la base de datos (se crea sola si no existe)
    return sqlite3.connect("powen_data.db", check_same_thread=False)

conn = get_connection()

# --- ¡CORRECCIÓN CLAVE! ---
# Creamos la estructura de la tabla SIEMPRE al iniciar, por si es un servidor nuevo
conn.execute('''
    CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proyecto TEXT,
        potencia REAL,
        ubicacion TEXT,
        vendedor TEXT
    )
''')
conn.commit()
# ---------------------------

# --- NAVEGACIÓN LATERAL ---
# Intentamos mostrar el logo, si falla (por internet), mostramos texto
try:
    st.sidebar.image("https://powen.mx/wp-content/uploads/2023/05/Logo-Powen-Negro.png", width=150)
except:
    st.sidebar.header("POWEN")

menu = st.sidebar.radio("MENÚ PRINCIPAL", ["📊 Dashboard", "➕ Registro de Proyectos", "🗺️ Mapa de Operaciones"])

# --- SECCIÓN 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("📊 Panel de Control Fotovoltaico")
    
    # Ahora sí, es seguro leer porque la tabla ya existe
    df = pd.read_sql_query("SELECT * FROM proyectos", conn)
    
    if not df.empty:
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Proyectos Totales", len(df))
        c2.metric("Potencia Instalada", f"{df['potencia'].sum():,.2f} kW")
        c3.metric("Ubicaciones Activas", df['ubicacion'].nunique())
        
        st.divider()
        
        col_graf, col_tabla = st.columns([1, 2])
        with col_graf:
            st.subheader("Potencia por Ubicación")
            st.bar_chart(df.groupby("ubicacion")["potencia"].sum())
        
        with col_tabla:
            st.subheader("Detalle de Proyectos")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("👋 ¡Bienvenido al sistema en la nube! La base de datos está limpia. Ve a la pestaña 'Registro' para añadir tu primer proyecto.")

# --- SECCIÓN 2: REGISTRO ---
elif menu == "➕ Registro de Proyectos":
    st.title("➕ Alta de Nuevos Proyectos")
    st.markdown("---")
    
    with st.form("form_registro", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre del Proyecto (Cliente/Sitio)")
        potencia = col2.number_input("Capacidad Instalada (kW)", min_value=0.0, step=0.1)
        ubicacion = col1.selectbox("Estado de la República", ["CDMX", "Edomex", "Querétaro", "Jalisco", "Nuevo León", "Yucatán", "Puebla"])
        vendedor = col2.text_input("Responsable del Proyecto")
        
        submitted = st.form_submit_button("💾 Guardar en Base de Datos")
        
        if submitted:
            if nombre and potencia > 0:
                conn.execute("INSERT INTO proyectos (proyecto, potencia, ubicacion, vendedor) VALUES (?,?,?,?)",
                             (nombre, potencia, ubicacion, vendedor))
                conn.commit()
                st.success(f"✅ ¡Éxito! El proyecto '{nombre}' ya está en la nube.")
                # Botón para recargar y ver el cambio (opcional)
                st.rerun()
            else:
                st.error("⚠️ Por favor ingresa al menos el Nombre y la Potencia.")

# --- SECCIÓN 3: MAPA ---
elif menu == "🗺️ Mapa de Operaciones":
    st.title("🗺️ Cobertura Nacional")
    st.write("Próximamente visualización geoespacial.")