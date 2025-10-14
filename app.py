import streamlit as st
from views.public_chat import public_chat
from utils.theme_utils import apply_global_theme
from models.db import init_database
from utils.vector_functions import initialize_sample_collection

# Page configuration
st.set_page_config(
    page_title="EcoMarket - Asistente Virtual",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    # Ejecutar setup completo
    from setup import setup
    setup()
    
    # Inicializar la base de datos
    init_database()
    
    # Inicializar documentos de muestra
    with st.spinner("🔄 Cargando documentos de muestra..."):
        success = initialize_sample_collection()
        if success:
            st.success("✅ Documentos de muestra cargados correctamente")
        else:
            st.warning("⚠️ Algunos documentos de muestra no se pudieron cargar")
    
    # Aplicar tema global
    apply_global_theme()
    
    # Ejecutar la aplicación principal
    public_chat()