#!/usr/bin/env python3
"""
Script para configurar OpenAI y completar la inicialización de la base de datos vectorial
"""

import os
import sys

def setup_openai_key():
    """Configurar la API key de OpenAI"""
    print("=" * 60)
    print("🔑 CONFIGURACIÓN DE OPENAI API KEY")
    print("=" * 60)
    print()
    
    # Verificar si ya existe
    current_key = os.environ.get('OPENAI_API_KEY')
    if current_key:
        print(f"✅ API key ya configurada: {current_key[:10]}...")
        return True
    
    print("Para que la aplicación funcione completamente, necesitas configurar tu API key de OpenAI.")
    print("Puedes obtener una API key gratuita en: https://platform.openai.com/api-keys")
    print()
    
    # Intentar leer desde archivo .env
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"📄 Archivo .env encontrado: {env_file}")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content:
                    print("✅ OPENAI_API_KEY encontrada en .env")
                    return True
        except Exception as e:
            print(f"⚠️  Error leyendo .env: {e}")
    
    # Crear archivo .env si no existe
    print(f"📝 Creando archivo {env_file}...")
    try:
        api_key = input("Ingresa tu API key de OpenAI (o presiona Enter para omitir): ").strip()
        
        if api_key:
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print(f"✅ API key guardada en {env_file}")
            
            # Configurar variable de entorno para esta sesión
            os.environ['OPENAI_API_KEY'] = api_key
            return True
        else:
            print("⚠️  API key no configurada. La aplicación funcionará pero sin capacidades de IA.")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Configuración cancelada")
        return False
    except Exception as e:
        print(f"❌ Error configurando API key: {e}")
        return False

def complete_vector_initialization():
    """Completar la inicialización de la base de datos vectorial"""
    print("\n" + "=" * 60)
    print("🔨 COMPLETANDO INICIALIZACIÓN VECTORIAL")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import initialize_sample_collection
        
        print("🔄 Inicializando colección de documentos de muestra...")
        success = initialize_sample_collection()
        
        if success:
            print("✅ Colección vectorial inicializada exitosamente")
            return True
        else:
            print("❌ Error inicializando colección vectorial")
            return False
            
    except Exception as e:
        print(f"❌ Error en inicialización vectorial: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_system():
    """Probar el sistema completo"""
    print("\n" + "=" * 60)
    print("🧪 PROBANDO SISTEMA COMPLETO")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        print("🔍 Creando retriever...")
        retriever = get_combined_retriever()
        print("✅ Retriever creado exitosamente")
        
        # Probar consultas
        test_queries = [
            "¿Cuál es la política de devoluciones?",
            "¿Qué productos hay en el inventario?",
            "¿Cuáles son las preguntas frecuentes?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Probando: {query}")
            try:
                docs = retriever.get_relevant_documents(query)
                print(f"  📊 Documentos relevantes: {len(docs)}")
                
                if docs:
                    for i, doc in enumerate(docs[:1]):  # Solo el primero
                        print(f"    Documento {i+1}: {doc.page_content[:100]}...")
                else:
                    print("    ⚠️  No se encontraron documentos relevantes")
                    
            except Exception as e:
                print(f"    ❌ Error en consulta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando sistema: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Configurando OpenAI y completando inicialización...")
    print()
    
    # 1. Configurar API key
    api_configured = setup_openai_key()
    
    if not api_configured:
        print("\n⚠️  API key no configurada. Continuando sin capacidades de IA...")
        print("Los documentos aparecerán en el panel de admin pero las consultas no funcionarán.")
        return
    
    # 2. Completar inicialización vectorial
    vector_success = complete_vector_initialization()
    
    if not vector_success:
        print("\n❌ Error en inicialización vectorial")
        return
    
    # 3. Probar sistema completo
    test_success = test_complete_system()
    
    if test_success:
        print("\n🎉 ¡Sistema completamente configurado!")
        print("Los documentos de muestra están listos y las consultas deberían funcionar.")
    else:
        print("\n⚠️  Sistema configurado pero con problemas en las consultas")

if __name__ == "__main__":
    main()
