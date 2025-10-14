#!/usr/bin/env python3
"""
Script para probar el sistema con API key de OpenAI
"""

import os
import sys

def main():
    """Función principal"""
    print("🚀 Probando sistema con API key de OpenAI...")
    print()
    
    # Configurar API key (reemplaza con tu clave real)
    api_key = "sk-your-actual-api-key-here"  # Reemplaza con tu API key real
    
    if api_key == "sk-your-actual-api-key-here":
        print("⚠️  Por favor, configura tu API key de OpenAI en este script")
        print("Obtén una API key gratuita en: https://platform.openai.com/api-keys")
        return
    
    # Configurar variable de entorno
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Importar y ejecutar el test final
    try:
        from final_test import main as test_main
        test_main()
    except Exception as e:
        print(f"❌ Error ejecutando test: {e}")

if __name__ == "__main__":
    main()
