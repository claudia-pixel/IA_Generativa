#!/usr/bin/env python3
"""
Script de diagnóstico simple para verificar archivos y base de datos
"""

import os
import sys
import glob
import sqlite3

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
        conn = sqlite3.connect("doc_sage.sqlite")
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

def check_vector_persist_directory():
    """Verificar el directorio de persistencia vectorial"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO DIRECTORIO DE PERSISTENCIA")
    print("=" * 60)
    
    persist_dir = "./static/persist"
    if not os.path.exists(persist_dir):
        print(f"❌ Directorio persist no existe: {persist_dir}")
        return False
    
    print(f"✅ Directorio persist existe: {persist_dir}")
    
    # Listar archivos
    files = os.listdir(persist_dir)
    print(f"📋 Archivos en persist: {files}")
    
    # Verificar archivos específicos de ChromaDB
    chroma_files = [f for f in files if 'chroma' in f.lower() or f.endswith('.sqlite3')]
    if chroma_files:
        print(f"✅ Archivos de ChromaDB encontrados: {chroma_files}")
    else:
        print("❌ No se encontraron archivos de ChromaDB")
    
    return len(chroma_files) > 0

def check_docker_volumes():
    """Verificar si estamos en Docker y los volúmenes están montados"""
    print("\n" + "=" * 60)
    print("🐳 VERIFICANDO ENTORNO DOCKER")
    print("=" * 60)
    
    # Verificar variables de entorno de Docker
    docker_container = os.environ.get('DOCKER_CONTAINER', False)
    print(f"🐳 DOCKER_CONTAINER: {docker_container}")
    
    # Verificar si los archivos están en el lugar correcto
    sample_dir = "./static/sample_documents"
    if os.path.exists(sample_dir):
        files = os.listdir(sample_dir)
        print(f"📁 Archivos en {sample_dir}: {files}")
        
        # Verificar permisos
        for file in files:
            file_path = os.path.join(sample_dir, file)
            if os.path.isfile(file_path):
                readable = os.access(file_path, os.R_OK)
                print(f"  {file}: {'✅ Legible' if readable else '❌ No legible'}")
    
    return True

def main():
    """Función principal de diagnóstico"""
    print("🚀 Iniciando diagnóstico simple de documentos de muestra...")
    print()
    
    # Verificaciones paso a paso
    checks = [
        ("Directorio de documentos", check_sample_documents_directory),
        ("Base de datos", check_database_sources),
        ("Directorio de persistencia", check_vector_persist_directory),
        ("Entorno Docker", check_docker_volumes)
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
