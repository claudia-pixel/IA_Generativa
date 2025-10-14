import streamlit as st
import time
import os
from db import create_message, get_messages
from vector_functions import load_retriever, generate_answer_from_context

def stream_response(response):
    """Stream response word by word"""
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

def public_chat():
    """Public chat interface for customers"""
    
    # Custom CSS for branding
    st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #2E7D32;
            padding: 20px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .welcome-box {
            background-color: #E8F5E9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("<h1 class='main-header'>🌿 EcoMarket - Asistente Virtual</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Tu compañero para productos sostenibles</p>", unsafe_allow_html=True)
    
    # Welcome message
    if "messages_loaded" not in st.session_state:
        st.session_state.messages_loaded = True
        with st.container():
            st.markdown("""
                <div class='welcome-box'>
                    <h3>👋 ¡Bienvenido a EcoMarket!</h3>
                    <p>Estoy aquí para ayudarte con:</p>
                    <ul>
                        <li>📦 Estado de pedidos y envíos</li>
                        <li>🔄 Políticas de devolución y cambio</li>
                        <li>🌱 Información sobre productos sostenibles</li>
                        <li>💳 Métodos de pago y facturación</li>
                        <li>❓ Preguntas frecuentes</li>
                    </ul>
                    <p><strong>¿En qué puedo ayudarte hoy?</strong></p>
                </div>
            """, unsafe_allow_html=True)
    
    # Chat history (using chat_id = 2 for public chat)
    CHAT_ID = 2
    
    # Load messages
    messages = get_messages(CHAT_ID)
    
    # Display chat history
    if messages:
        for sender, content in messages:
            if sender == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            elif sender == "ai":
                with st.chat_message("assistant", avatar="🌿"):
                    st.markdown(content)
    
    # Chat input
    prompt = st.chat_input("Escribe tu pregunta aquí...")
    
    if prompt:
        # Save user message
        create_message(CHAT_ID, "user", prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Load retriever
        collection_name = "ecomarket_kb"
        
        try:
            # Verificar si existe la base de datos ChromaDB
            if os.path.exists("./persist/chroma.sqlite3"):
                retriever = load_retriever(collection_name=collection_name)
                
                # Generate response
                response = generate_answer_from_context(retriever, prompt)
            else:
                response = """
                🙏 Disculpa, actualmente estamos configurando nuestro sistema de respuestas automáticas.
                
                Por favor, contacta directamente con nuestro equipo de soporte:
                - 📧 Email: soporte@ecomarket.com
                - 📞 Teléfono: +57 123 456 7890
                - ⏰ Horario: Lunes a Viernes 9:00 AM - 6:00 PM
                """
        except Exception as e:
            response = """
            😔 Lo siento, tuve un problema al procesar tu consulta.
            
            Por favor, intenta nuevamente o contacta a nuestro equipo:
            - 📧 soporte@ecomarket.com
            - 📞 +57 123 456 7890
            """
        
        # Save AI response
        create_message(CHAT_ID, "ai", response)
        
        # Display AI response with streaming
        with st.chat_message("assistant", avatar="🌿"):
            st.write_stream(stream_response(response))
        
        st.rerun()
    
    # Sidebar with info
    with st.sidebar:
        st.markdown("### 📞 Contacto Directo")
        st.markdown("""
            Si necesitas asistencia personalizada:
            
            **Email:** ceman217@gmail.com
            
            **Teléfono:** +57 300 733 5302
            
            **WhatsApp:** +57 300 733 5302
            
            **Horario de atención:**
            Lunes a Viernes: 9:00 AM - 6:00 PM
            Sábados: 10:00 AM - 2:00 PM
        """)
        
        st.markdown("---")
        
        st.markdown("### 🌿 Sobre EcoMarket")
        st.markdown("""
            Somos tu tienda de productos sostenibles, 
            comprometidos con el medio ambiente y 
            la calidad de vida.
        """)
        
        st.markdown("---")
        


if __name__ == "__main__":
    public_chat()