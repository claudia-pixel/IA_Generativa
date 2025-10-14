import streamlit as st
from public_chat import public_chat

# Page configuration
st.set_page_config(
    page_title="EcoMarket - Asistente Virtual",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

if __name__ == "__main__":
    public_chat()