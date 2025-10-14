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
    # La inicialización se hace en init_app.py antes de ejecutar la aplicación
    # Solo inicializar la base de datos si es necesario
    init_database()
    
    # Aplicar tema global
    apply_global_theme()
    
    # Ejecutar la aplicación principal
    public_chat()