#!/usr/bin/env python3
"""
Script para forzar la inicialización de documentos de muestra
"""

import os
import sys
import shutil
from models.db import init_database, connect_db
from utils.vector_functions import (
    load_sample_documents,
    create_collection,
    register_sample_documents_in_db
)

def clear_existing_data():
    """Limpiar datos existentes para forzar reinicialización"""
    print("🧹 Limpiando datos existentes...")
    
    # Limpiar directorio persist
    persist_dir = "./static/persist"
    if os.path.exists(persist_dir):
        print(f"🗑️  Eliminando directorio persist: {persist_dir}")
        shutil.rmtree(persist_dir)
    
    # Recrear directorio
    os.makedirs(persist_dir, exist_ok=True)
    print("✅ Directorio persist recreado")
    
    # Limpiar fuentes de muestra de la base de datos
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sources WHERE type = 'sample_document'")
        conn.commit()
        conn.close()
        print("✅ Fuentes de muestra eliminadas de la base de datos")
    except Exception as e:
        print(f"⚠️  Error limpiando base de datos: {e}")

def force_initialize_documents():
    """Forzar la inicialización de documentos"""
    print("=" * 60)
    print("🚀 INICIALIZACIÓN FORZADA DE DOCUMENTOS")
    print("=" * 60)
    print()
    
    # 1. Limpiar datos existentes
    clear_existing_data()
    print()
    
    # 2. Verificar que los archivos existen
    sample_dir = "./static/sample_documents"
    if not os.path.exists(sample_dir):
        print(f"❌ Directorio de documentos no existe: {sample_dir}")
        return False
    
    files = os.listdir(sample_dir)
    print(f"📁 Archivos encontrados: {files}")
    
    if not files:
        print("❌ No hay archivos de muestra")
        return False
    
    # 3. Cargar documentos
    print("\n📚 Cargando documentos de muestra...")
    try:
        documents, collection_name = load_sample_documents()
        print(f"✅ Cargados {len(documents)} documentos")
        
        if not documents:
            print("❌ No se pudieron cargar los documentos")
            return False
        
        # Mostrar información de los documentos
        for i, doc in enumerate(documents):
            print(f"  Documento {i+1}: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:100]}...")
            print(f"    Metadatos: {doc.metadata}")
            print()
        
    except Exception as e:
        print(f"❌ Error cargando documentos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Crear colección vectorial
    print("🔨 Creando colección vectorial...")
    try:
        persist_directory = "./static/persist"
        os.makedirs(persist_directory, exist_ok=True)
        
        vectordb = create_collection(collection_name, documents)
        if not vectordb:
            print("❌ Error creando colección vectorial")
            return False
        
        print("✅ Colección vectorial creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando colección: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Registrar en base de datos
    print("\n📝 Registrando documentos en base de datos...")
    try:
        register_sample_documents_in_db()
        print("✅ Documentos registrados en base de datos")
        
    except Exception as e:
        print(f"❌ Error registrando en base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Verificar resultado
    print("\n🔍 Verificando resultado...")
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sources WHERE type = 'sample_document'")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📊 Documentos registrados en DB: {count}")
        
        if count > 0:
            print("✅ Inicialización completada exitosamente")
            return True
        else:
            print("❌ No se registraron documentos en la base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando resultado: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando inicialización forzada de documentos...")
    print()
    
    success = force_initialize_documents()
    
    if success:
        print("\n🎉 ¡Inicialización forzada completada exitosamente!")
        print("Los documentos de muestra deberían aparecer ahora en el panel de admin.")
    else:
        print("\n❌ La inicialización forzada falló")

if __name__ == "__main__":
    main()
