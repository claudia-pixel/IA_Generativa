"""
Script de configuración inicial para EcoMarket RAG System
Ejecutar este script antes de iniciar la aplicación por primera vez
"""

import os
from db import init_database
from auth import create_admin_table, create_admin_user

def setup():
    """Initialize the system"""
    
    print("=" * 60)
    print("🌿 ECOMARKET RAG SYSTEM - CONFIGURACIÓN INICIAL")
    print("=" * 60)
    print()
    
    # Create directories
    print("📁 Creando directorios necesarios...")
    os.makedirs("persist", exist_ok=True)
    os.makedirs("temp_files", exist_ok=True)
    os.makedirs("pages", exist_ok=True)
    print("✅ Directorios creados")
    print()
    
    # Initialize database
    print("🗄️  Inicializando base de datos...")
    init_database()
    create_admin_table()
    print("✅ Base de datos inicializada")
    print()
    
    # Create admin user
    print("👤 Configuración de usuario administrador")
    print("-" * 60)
    
    default_username = "admin"
    default_password = "adminecomarket2025"
    default_email = "admin@ecomarket.com"
    
    print(f"Usuario por defecto: {default_username}")
    print(f"Contraseña por defecto: {default_password}")
    print(f"Email: {default_email}")
    print()
    
    change = input("¿Deseas cambiar las credenciales? (s/n): ").lower()
    
    if change == 's':
        username = input("Nuevo usuario: ").strip()
        password = input("Nueva contraseña: ").strip()
        email = input("Email: ").strip()
        
        if not username or not password:
            print("❌ Usuario y contraseña son obligatorios")
            return
    else:
        username = default_username
        password = default_password
        email = default_email
    
    # Create admin user
    if create_admin_user(username, password, email):
        print()
        print("✅ Usuario administrador creado exitosamente!")
        print()
        print("=" * 60)
        print("📋 CREDENCIALES DE ACCESO")
        print("=" * 60)
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print(f"Email: {email}")
        print("=" * 60)
        print()
        print("⚠️  IMPORTANTE: Guarda estas credenciales en un lugar seguro")
        print()
    else:
        print("❌ Error: El usuario ya existe")
        print()
    
    # Instructions
    print("=" * 60)
    print("🚀 SIGUIENTE PASO")
    print("=" * 60)
    print()
    print("Para iniciar la aplicación, ejecuta:")
    print()
    print("  streamlit run app.py")
    print()
    print("Accesos:")
    print("  • Chat Público: http://localhost:8501")
    print("  • Panel Admin: Clic en 'Panel de Admin' en el chat")
    print()
    print("=" * 60)
    print()

if __name__ == "__main__":
    setup()