# --- CONFIGURACIÓN DE PÁGINA Y LOGO ---
# Cambiamos el título de la pestaña y el ícono a una fábrica 🏭
st.set_page_config(page_title="POWEN INDUSTRIAL", layout="wide", page_icon="🏭")

# Asegúrate de que tu imagen del logo se llame "logo.png" en la carpeta
st.logo("logo.png")

# ... (El resto de las importaciones y conexión a DB sigue igual) ...

# --- SECCIÓN: DASHBOARD ---
if menu == "📊 Dashboard":
    # Aquí cambiamos el título grande que se ve en la pantalla
    st.title("🏭 POWEN INDUSTRIAL") 
    st.markdown("**Panel de Control de Proyectos B2B**") # Subtítulo opcional elegante
    
    # ... (El resto del código del dashboard sigue igual) ...