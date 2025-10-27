"""
Google OAuth Login View with OTP Verification
"""
import streamlit as st
import os
import httpx
from controllers.auth import (
    authenticate_google_user, 
    verify_google_otp, 
    create_google_session,
    get_google_user_by_email
)
from utils.theme_utils import apply_theme_with_header
from models.db import init_database
import time


def google_login():
    """Google OAuth login page with OTP verification"""
    
    # Initialize database
    init_database()
    
    # Apply theme
    apply_theme_with_header()
    
    # Initialize session state
    if 'google_user' not in st.session_state:
        st.session_state.google_user = None
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'email' not in st.session_state:
        st.session_state.email = None
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h2 class='login-header'>🔐 Iniciar Sesión con Google</h2>", unsafe_allow_html=True)
        
        # If we have a callback from Google
        if 'code' in st.query_params:
            # Check if we haven't already processed this
            if 'google_callback_processed' not in st.session_state:
                try:
                    code = st.query_params['code']
                    st.session_state.google_callback_processed = True
                    
                    # Exchange code for token
                    from tools.google_auth import google_auth_service
                    
                    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", 
                                             f"{os.getenv('APP_URL', 'http://localhost:8501')}/google_login")
                    
                    token_data = google_auth_service.exchange_code_for_token(code, redirect_uri)
                    
                    if token_data:
                        # Get user info
                        user_info = google_auth_service.get_user_info_from_token(token_data['access_token'])
                        
                        if user_info:
                            # Authenticate user and send OTP
                            auth_result = authenticate_google_user(user_info)
                            
                            if auth_result.get('success'):
                                st.session_state.email = user_info['email']
                                st.session_state.google_user = user_info
                                st.session_state.otp_sent = True
                                
                                st.success("✅ Código OTP enviado a tu correo electrónico")
                                time.sleep(2)
                                # Clean query params by redirecting without them
                                st.query_params.clear()
                                st.rerun()
                            else:
                                st.error(f"❌ {auth_result.get('message')}")
                        else:
                            st.error("❌ No se pudo obtener información del usuario")
                    else:
                        st.error("❌ Error al autenticar con Google")
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
        
        # OTP verification form
        elif st.session_state.otp_sent and st.session_state.email:
            st.markdown(f"<p style='text-align: center;'>Enviado a: <strong>{st.session_state.email}</strong></p>", 
                       unsafe_allow_html=True)
            
            with st.form("otp_form"):
                otp_code = st.text_input(
                    "Código OTP", 
                    placeholder="Ingresa el código de 6 dígitos",
                    max_chars=6
                )
                
                submit = st.form_submit_button("Verificar", type="primary", use_container_width=True)
                
                if submit:
                    if otp_code and len(otp_code) == 6:
                        # Verify OTP
                        if verify_google_otp(st.session_state.email, otp_code):
                            # Create session
                            session_token = create_google_session(st.session_state.google_user)
                            
                            st.session_state.session_token = session_token
                            st.session_state.user_info = {
                                "email": st.session_state.google_user["email"],
                                "username": st.session_state.google_user["email"],
                                "name": st.session_state.google_user.get("name"),
                                "picture": st.session_state.google_user.get("picture")
                            }
                            
                            st.success("✅ Verificación exitosa!")
                            st.balloons()
                            time.sleep(1)
                            st.switch_page("views/admin_panel.py")
                        else:
                            st.error("❌ Código OTP incorrecto o expirado")
                    else:
                        st.warning("⚠️ Por favor ingresa un código de 6 dígitos")
            
            # Resend OTP
            if st.button("🔄 Reenviar código", use_container_width=True):
                if st.session_state.email:
                    from controllers.auth import send_google_otp
                    if send_google_otp(st.session_state.email):
                        st.success("✅ Código reenviado")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error al reenviar código")
        
        # Google OAuth button
        else:
            st.markdown("<p style='text-align: center; color: var(--text-color); margin-bottom: 30px;'>"
                       "Autenticación con Google + Verificación OTP</p>", unsafe_allow_html=True)
            
            # Google Login Button
            from tools.google_auth import google_auth_service
            
            redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", 
                                   f"{os.getenv('APP_URL', 'http://localhost:8501')}/google_login")
            
            auth_url, state = google_auth_service.generate_auth_url(redirect_uri)
            
            # Store state in session
            st.session_state.oauth_state = state
            
            # Create Google button
            st.markdown("""
                <style>
                .google-login-button {
                    background-color: #4285f4;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    width: 100%;
                }
                .google-login-button:hover {
                    background-color: #357ae8;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.link_button(
                "🔵 Continuar con Google",
                auth_url,
                use_container_width=True,
                type="primary"
            )
        
        st.markdown("---")
        
        # Back to login options
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔐 Login Administrador", use_container_width=True):
                st.switch_page("views/admin_login.py")
        
        with col_b:
            if st.button("← Volver al Chat", use_container_width=True):
                st.switch_page("app.py")


if __name__ == "__main__":
    google_login()

