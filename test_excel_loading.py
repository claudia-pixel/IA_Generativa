#!/usr/bin/env python3
"""
Script de prueba específico para verificar la carga del archivo Excel.
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.vector_functions import load_document, load_retriever, generate_answer_from_context

def test_excel_loading():
    """Test loading the Excel file specifically"""
    print("=" * 60)
    print("🧪 PRUEBA DE CARGA DE ARCHIVO EXCEL")
    print("=" * 60)
    print()
    
    excel_file = "./static/sample_documents/Inventario_Sostenible.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Archivo no encontrado: {excel_file}")
        return False
    
    try:
        print(f"📄 Cargando archivo: {excel_file}")
        documents = load_document(excel_file)
        
        print(f"✅ Cargados {len(documents)} documentos del archivo Excel")
        
        # Mostrar contenido de cada documento
        for i, doc in enumerate(documents):
            print(f"\n--- Documento {i+1} ---")
            print(f"Contenido: {doc.page_content[:200]}...")
            print(f"Metadatos: {doc.metadata}")
        
        # Probar consulta específica
        print(f"\n🔍 Probando consulta sobre cargador solar...")
        
        # Crear colección temporal para prueba
        from utils.vector_functions import create_collection
        vectordb = create_collection("test_collection", documents)
        
        if vectordb:
            retriever = load_retriever("test_collection")
            
            # Probar consulta
            query = "Cuanto cuesta un Cargador Solar Portátil?"
            print(f"Pregunta: {query}")
            
            response = generate_answer_from_context(retriever, query)
            print(f"Respuesta: {response}")
            
            return True
        else:
            print("❌ No se pudo crear la colección de prueba")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_loading()
    if success:
        print("\n✅ Prueba exitosa")
    else:
        print("\n❌ Prueba falló")
