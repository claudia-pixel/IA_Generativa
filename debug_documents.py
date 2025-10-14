#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la carga de documentos de muestra
"""

import os
import sys
import glob
from models.db import connect_db, list_sources
from utils.vector_functions import (
    load_sample_documents, 
    is_sample_collection_initialized,
    load_collection,
    get_combined_retriever
)

def check_sample_documents_directory():
    """Verificar que el directorio de documentos de muestra existe y tiene archivos"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE DOCUMENTOS DE MUESTRA")
    print("=" * 60)
    print()
    
    sample_dir = "./static/sample_documents"
    print(f"📁 Verificando directorio: {sample_dir}")
    
    if not os.path.exists(sample_dir):
        print(f"❌ El directorio {sample_dir} no existe")
        return False
    
    print(f"✅ El directorio {sample_dir} existe")
    
    # Listar archivos
    all_files = os.listdir(sample_dir)
    print(f"📋 Archivos encontrados: {all_files}")
    
    # Verificar archivos específicos
    expected_files = [
        "Inventario_Sostenible.xlsx",
        "politica_devoluciones.txt", 
        "preguntas_frecuentes.txt"
    ]
    
    for file in expected_files:
        file_path = os.path.join(sample_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file} - Existe")
        else:
            print(f"❌ {file} - No encontrado")
    
    return len(all_files) > 0

def check_database_sources():
    """Verificar qué documentos están registrados en la base de datos"""
    print("\n" + "=" * 60)
    print("🗄️  VERIFICANDO BASE DE DATOS")
    print("=" * 60)
    
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tablas en la base de datos: {[table[0] for table in tables]}")
        
        # Verificar fuentes
        cursor.execute("SELECT COUNT(*) FROM sources")
        total_sources = cursor.fetchone()[0]
        print(f"📊 Total de fuentes en la base de datos: {total_sources}")
        
        # Verificar fuentes de muestra
        cursor.execute("SELECT COUNT(*) FROM sources WHERE type = 'sample_document'")
        sample_sources = cursor.fetchone()[0]
        print(f"🌿 Fuentes de muestra: {sample_sources}")
        
        # Listar fuentes de muestra
        cursor.execute("SELECT name, source_text FROM sources WHERE type = 'sample_document'")
        sample_docs = cursor.fetchall()
        print(f"📄 Documentos de muestra registrados:")
        for doc in sample_docs:
            print(f"  - {doc[0]}: {doc[1][:50] if doc[1] else 'Sin descripción'}...")
        
        conn.close()
        return sample_sources > 0
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def check_vector_collection():
    """Verificar la colección vectorial"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO COLECCIÓN VECTORIAL")
    print("=" * 60)
    
    try:
        # Verificar si la colección está inicializada
        is_initialized = is_sample_collection_initialized()
        print(f"📊 Colección inicializada: {is_initialized}")
        
        # Verificar directorio persist
        persist_dir = "./static/persist"
        if os.path.exists(persist_dir):
            print(f"✅ Directorio persist existe: {persist_dir}")
            files = os.listdir(persist_dir)
            print(f"📋 Archivos en persist: {files}")
        else:
            print(f"❌ Directorio persist no existe: {persist_dir}")
            return False
        
        # Intentar cargar la colección
        try:
            vectordb = load_collection("sample_documents")
            count = vectordb._collection.count()
            print(f"✅ Colección 'sample_documents' cargada - {count} documentos")
            return count > 0
        except Exception as e:
            print(f"❌ Error cargando colección: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando colección vectorial: {e}")
        return False

def test_document_loading():
    """Probar la carga de documentos"""
    print("\n" + "=" * 60)
    print("🧪 PROBANDO CARGA DE DOCUMENTOS")
    print("=" * 60)
    
    try:
        documents, collection_name = load_sample_documents()
        print(f"📊 Documentos cargados: {len(documents)}")
        print(f"📝 Nombre de colección: {collection_name}")
        
        if documents:
            for i, doc in enumerate(documents[:3]):  # Mostrar primeros 3
                print(f"  Documento {i+1}:")
                print(f"    Contenido: {doc.page_content[:100]}...")
                print(f"    Metadatos: {doc.metadata}")
                print()
        
        return len(documents) > 0
        
    except Exception as e:
        print(f"❌ Error cargando documentos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_retriever():
    """Probar el retriever"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO RETRIEVER")
    print("=" * 60)
    
    try:
        retriever = get_combined_retriever()
        print("✅ Retriever creado exitosamente")
        
        # Probar una consulta
        test_query = "¿Cuál es la política de devoluciones?"
        print(f"🔍 Probando consulta: {test_query}")
        
        docs = retriever.get_relevant_documents(test_query)
        print(f"📊 Documentos relevantes encontrados: {len(docs)}")
        
        for i, doc in enumerate(docs[:2]):
            print(f"  Documento {i+1}: {doc.page_content[:100]}...")
        
        return len(docs) > 0
        
    except Exception as e:
        print(f"❌ Error probando retriever: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de diagnóstico"""
    print("🚀 Iniciando diagnóstico de documentos de muestra...")
    print()
    
    # Verificaciones paso a paso
    checks = [
        ("Directorio de documentos", check_sample_documents_directory),
        ("Base de datos", check_database_sources),
        ("Colección vectorial", check_vector_collection),
        ("Carga de documentos", test_document_loading),
        ("Retriever", test_retriever)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'='*20} {name.upper()} {'='*20}")
        result = check_func()
        results.append((name, result))
        print(f"Resultado: {'✅ ÉXITO' if result else '❌ FALLO'}")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"\n📈 Éxito: {success_count}/{total_count} verificaciones")
    
    if success_count == total_count:
        print("🎉 ¡Todos los sistemas funcionan correctamente!")
    else:
        print("⚠️  Hay problemas que necesitan ser resueltos")

if __name__ == "__main__":
    main()
