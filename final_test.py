#!/usr/bin/env python3
"""
Script de prueba final para verificar que todo funciona correctamente
"""

import os
import sys
import sqlite3

def test_database():
    """Probar la base de datos"""
    print("🗄️  Probando base de datos...")
    
    try:
        conn = sqlite3.connect("doc_sage.sqlite")
        cursor = conn.cursor()
        
        # Verificar fuentes de muestra
        cursor.execute("SELECT COUNT(*) FROM sources WHERE type = 'sample_document'")
        count = cursor.fetchone()[0]
        print(f"  📊 Documentos de muestra en DB: {count}")
        
        if count > 0:
            cursor.execute("SELECT name FROM sources WHERE type = 'sample_document'")
            docs = cursor.fetchall()
            print(f"  📄 Documentos: {[doc[0] for doc in docs]}")
        
        conn.close()
        return count > 0
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_files():
    """Probar archivos de muestra"""
    print("📁 Probando archivos de muestra...")
    
    sample_dir = "./static/sample_documents"
    if not os.path.exists(sample_dir):
        print(f"  ❌ Directorio no existe: {sample_dir}")
        return False
    
    files = os.listdir(sample_dir)
    print(f"  📋 Archivos encontrados: {files}")
    
    expected_files = [
        "Inventario_Sostenible.xlsx",
        "politica_devoluciones.txt",
        "preguntas_frecuentes.txt"
    ]
    
    all_exist = True
    for file in expected_files:
        if file in files:
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - No encontrado")
            all_exist = False
    
    return all_exist

def test_vector_persist():
    """Probar directorio de persistencia vectorial"""
    print("🔍 Probando persistencia vectorial...")
    
    persist_dir = "./static/persist"
    if not os.path.exists(persist_dir):
        print(f"  ❌ Directorio no existe: {persist_dir}")
        return False
    
    files = os.listdir(persist_dir)
    print(f"  📋 Archivos en persist: {files}")
    
    chroma_files = [f for f in files if 'chroma' in f.lower() or f.endswith('.sqlite3')]
    if chroma_files:
        print(f"  ✅ Archivos de ChromaDB: {chroma_files}")
        return True
    else:
        print("  ⚠️  No se encontraron archivos de ChromaDB")
        return False

def test_openai_config():
    """Probar configuración de OpenAI"""
    print("🔑 Probando configuración de OpenAI...")
    
    # Verificar variable de entorno
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print(f"  ✅ API key configurada: {api_key[:10]}...")
        return True
    
    # Verificar archivo .env
    env_file = ".env"
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY' in content:
                    print("  ✅ API key encontrada en .env")
                    return True
        except Exception as e:
            print(f"  ⚠️  Error leyendo .env: {e}")
    
    print("  ⚠️  API key no configurada")
    return False

def test_retriever():
    """Probar el retriever (si está disponible)"""
    print("🔍 Probando retriever...")
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        retriever = get_combined_retriever()
        print("  ✅ Retriever creado exitosamente")
        
        # Probar consulta
        test_query = "¿Cuál es la política de devoluciones?"
        docs = retriever.get_relevant_documents(test_query)
        print(f"  📊 Documentos relevantes para '{test_query}': {len(docs)}")
        
        return len(docs) > 0
        
    except Exception as e:
        print(f"  ⚠️  Error probando retriever: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🧪 PRUEBA FINAL DEL SISTEMA")
    print("=" * 60)
    print()
    
    tests = [
        ("Archivos de muestra", test_files),
        ("Base de datos", test_database),
        ("Persistencia vectorial", test_vector_persist),
        ("Configuración OpenAI", test_openai_config),
        ("Retriever", test_retriever)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*20} {name.upper()} {'='*20}")
        result = test_func()
        results.append((name, result))
        print(f"Resultado: {'✅ ÉXITO' if result else '❌ FALLO'}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if result:
            success_count += 1
    
    total_count = len(results)
    print(f"\n📈 Éxito: {success_count}/{total_count} pruebas")
    
    if success_count >= 3:  # Al menos archivos, DB y persistencia
        print("\n🎉 ¡Sistema funcionando correctamente!")
        print("Los documentos de muestra están listos y deberían aparecer en el panel de admin.")
        
        if success_count >= 4:  # Incluyendo OpenAI
            print("Las consultas de IA también deberían funcionar.")
        else:
            print("Para que funcionen las consultas de IA, configura la API key de OpenAI.")
    else:
        print("\n❌ El sistema tiene problemas que necesitan ser resueltos.")

if __name__ == "__main__":
    main()
