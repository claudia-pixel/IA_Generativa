import streamlit as st
import os
from auth import verify_session, logout_session
from db import create_source, list_sources, delete_source, connect_db
from vector_functions import (
    load_document,
    create_collection,
    load_collection,
    add_documents_to_collection,
)

def check_admin_auth():
    """Check if user is authenticated as admin"""
    if "session_token" not in st.session_state:
        return False
    
    user_info = verify_session(st.session_state.session_token)
    if user_info:
        st.session_state.user_info = user_info
        return True
    else:
        del st.session_state.session_token
        return False

def admin_panel():
    """Main admin panel for managing RAG knowledge base"""
    
    if not check_admin_auth():
        st.error("No autorizado. Por favor, inicia sesión.")
        if st.button("Ir a Login"):
            st.switch_page("pages/admin_login.py")
        return
    
    st.title("🔧 Panel de Administración - EcoMarket")
    st.write(f"Bienvenido, **{st.session_state.user_info['username']}**")
    
    # Logout button
    col1, col2 = st.columns([0.9, 0.1])
    with col2:
        if st.button("🚪 Salir"):
            logout_session(st.session_state.session_token)
            del st.session_state.session_token
            del st.session_state.user_info
            st.rerun()
    
    # Tabs for different management sections
    tab1, tab2, tab3 = st.tabs(["📚 Documentos", "📊 Estadísticas", "⚙️ Configuración"])
    
    with tab1:
        manage_documents()
    
    with tab2:
        show_statistics()
    
    with tab3:
        show_settings()

def manage_documents():
    """Document management interface"""
    
    st.subheader("Gestión de Base de Conocimiento")
    
    # Get system chat (chat_id = 1 reserved for system documents)
    collection_name = "ecomarket_kb"
    
    # Upload new document
    st.markdown("### 📤 Subir Nuevo Documento")
    
    with st.form("upload_form"):
        uploaded_file = st.file_uploader(
            "Selecciona un documento",
            type=["txt", "pdf", "docx", "csv", "html", "md"],
            help="Formatos soportados: TXT, PDF, DOCX, CSV, HTML, MD"
        )
        
        doc_description = st.text_area(
            "Descripción del documento",
            placeholder="Ej: Política de devoluciones actualizada 2024"
        )
        
        submit_button = st.form_submit_button("Subir Documento", type="primary")
        
        if submit_button and uploaded_file:
            with st.spinner("Procesando documento..."):
                try:
                    # Save temp file
                    temp_dir = "temp_files"
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                    
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Load document
                    document = load_document(temp_file_path)
                    
                    # Create or update collection
                    if not os.path.exists(f"./persist/{collection_name}"):
                        vectordb = create_collection(collection_name, document)
                    else:
                        vectordb = load_collection(collection_name)
                        vectordb = add_documents_to_collection(vectordb, document)
                    
                    # Save to database
                    create_source(
                        uploaded_file.name, 
                        doc_description, 
                        1,  # System chat
                        source_type="document"
                    )
                    
                    # Remove temp file
                    os.remove(temp_file_path)
                    
                    st.success(f"✅ Documento '{uploaded_file.name}' subido exitosamente!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error al procesar el documento: {str(e)}")
    
    # List existing documents
    st.markdown("### 📋 Documentos en el Sistema")
    
    documents = list_sources(1, source_type="document")
    
    if documents:
        st.write(f"Total de documentos: **{len(documents)}**")
        
        for doc in documents:
            doc_id = doc[0]
            doc_name = doc[1]
            doc_description = doc[2]
            
            with st.expander(f"📄 {doc_name}"):
                st.write(f"**Descripción:** {doc_description if doc_description else 'Sin descripción'}")
                
                col1, col2 = st.columns([0.8, 0.2])
                with col2:
                    if st.button("🗑️ Eliminar", key=f"delete_{doc_id}"):
                        delete_source(doc_id)
                        st.success(f"Documento eliminado: {doc_name}")
                        st.rerun()
    else:
        st.info("No hay documentos en el sistema. Sube el primer documento para comenzar.")

def show_statistics():
    """Show system statistics"""
    st.subheader("📊 Estadísticas del Sistema")
    
    conn = connect_db()
    cursor = conn.cursor()
    
    # Count documents
    cursor.execute("SELECT COUNT(*) FROM sources WHERE chat_id = 1 AND type = 'document'")
    doc_count = cursor.fetchone()[0]
    
    # Count customer queries (from public chat, chat_id = 2)
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 2 AND sender = 'user'")
    query_count = cursor.fetchone()[0]
    
    # Count AI responses
    cursor.execute("SELECT COUNT(*) FROM messages WHERE chat_id = 2 AND sender = 'ai'")
    response_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📚 Documentos", doc_count)
    
    with col2:
        st.metric("❓ Consultas Recibidas", query_count)
    
    with col3:
        st.metric("💬 Respuestas Generadas", response_count)
    
    st.markdown("---")
    
    # Recent queries
    st.markdown("### 🔍 Consultas Recientes")
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, timestamp 
        FROM messages 
        WHERE chat_id = 2 AND sender = 'user' 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    recent_queries = cursor.fetchall()
    conn.close()
    
    if recent_queries:
        for query, timestamp in recent_queries:
            st.text(f"[{timestamp}] {query[:100]}...")
    else:
        st.info("No hay consultas registradas aún.")

def show_settings():
    """Show system settings"""
    st.subheader("⚙️ Configuración del Sistema")
    
    st.markdown("### 🎯 Parámetros del RAG")
    
    # Score threshold setting
    score_threshold = st.slider(
        "Umbral de similitud",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.05,
        help="Valor mínimo de similitud para considerar un documento relevante"
    )
    
    st.info(f"Umbral actual: {score_threshold}")
    
    # Chunk size setting
    chunk_size = st.number_input(
        "Tamaño de fragmentos",
        min_value=100,
        max_value=2000,
        value=1000,
        step=100,
        help="Tamaño de los fragmentos de texto para procesamiento"
    )
    
    st.markdown("### 🔄 Mantenimiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpiar sesiones expiradas"):
            from auth import cleanup_expired_sessions
            cleanup_expired_sessions()
            st.success("Sesiones expiradas eliminadas")
    
    with col2:
        if st.button("📊 Exportar estadísticas"):
            st.info("Función de exportación en desarrollo")

if __name__ == "__main__":
    admin_panel()