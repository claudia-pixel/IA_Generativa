import streamlit as st
import time
from auth import verify_admin, create_session

def admin_login():
    """Admin login page"""
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
            padding: 30px;
            background-color: #f5f5f5;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            color: #2E7D32;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 class='login-header'>🔐 Admin Login</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>EcoMarket</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            
            submit = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)
            
            if submit:
                if username and password:
                    user_info = verify_admin(username, password)
                    
                    if user_info:
                        # Create session
                        session_token = create_session(user_info["id"])
                        st.session_state.session_token = session_token
                        st.session_state.user_info = user_info
                        
                        st.success("✅ Login exitoso!")
                        st.balloons()
                        time.sleep(1)
                        st.switch_page("pages/admin_panel.py")
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.warning("⚠️ Por favor ingresa usuario y contraseña")
        
        st.markdown("---")
        
        if st.button("← Volver al Chat Público", use_container_width=True):
            st.switch_page("app.py")

if __name__ == "__main__":
    admin_login()