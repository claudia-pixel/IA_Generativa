#!/usr/bin/env python3
"""
Script para probar el nuevo retriever con búsqueda por similitud
"""

import os
import sys

def test_new_retriever():
    """Probar el nuevo retriever"""
    print("🔍 PROBANDO NUEVO RETRIEVER")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Configurar API key si no está configurada
        if not os.environ.get('OPENAI_API_KEY'):
            print("⚠️  OPENAI_API_KEY no configurada")
            return False
        
        print("✅ API key configurada")
        
        # Crear retriever
        print("🔧 Creando retriever...")
        retriever = get_combined_retriever()
        print("✅ Retriever creado")
        
        # Consultas específicas para probar
        test_queries = [
            "Cargador Solar Portátil",
            "¿Cuánto cuesta el Cargador Solar Portátil?",
            "cargador solar",
            "lámpara solar",
            "productos de electrónica",
            "¿Qué productos hay en el inventario?",
            "productos con precio mayor a 40 dólares"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} CONSULTA {i} {'='*20}")
            print(f"🔍 Consulta: {query}")
            print("-" * 50)
            
            try:
                docs = retriever.get_relevant_documents(query)
                print(f"📊 Documentos encontrados: {len(docs)}")
                
                if docs:
                    for j, doc in enumerate(docs[:3]):  # Mostrar máximo 3
                        print(f"\n  📄 Documento {j+1}:")
                        print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
                        print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
                        print(f"    Contenido: {doc.page_content[:300]}...")
                        
                        # Verificar si contiene información relevante
                        content_lower = doc.page_content.lower()
                        if 'cargador' in content_lower and 'solar' in content_lower:
                            print("    ✅ ¡Contiene información sobre cargador solar!")
                        elif 'cargador' in content_lower:
                            print("    ⚠️  Contiene 'cargador' pero no 'solar'")
                        elif 'solar' in content_lower:
                            print("    ⚠️  Contiene 'solar' pero no 'cargador'")
                        elif 'inventario' in content_lower or 'excel' in doc.metadata.get('file_type', ''):
                            print("    📊 Contiene información del inventario")
                        else:
                            print("    ❌ No contiene información relevante")
                else:
                    print("  ❌ No se encontraron documentos relevantes")
                    
            except Exception as e:
                print(f"  ❌ Error en consulta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_similarity():
    """Probar búsqueda directa por similitud"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO BÚSQUEDA DIRECTA POR SIMILITUD")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_collection
        
        # Cargar colección
        vectordb = load_collection("sample_documents")
        
        # Probar búsqueda directa
        query = "Cargador Solar Portátil"
        print(f"🔍 Consulta: {query}")
        print("-" * 40)
        
        # Usar similarity_search directamente
        docs = vectordb.similarity_search(query, k=5)
        print(f"📊 Documentos encontrados: {len(docs)}")
        
        for i, doc in enumerate(docs):
            print(f"\n  📄 Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            
            # Verificar si contiene la consulta
            if "Cargador Solar Portátil" in doc.page_content:
                print("    ✅ ¡Contiene 'Cargador Solar Portátil'!")
            else:
                print("    ❌ No contiene 'Cargador Solar Portátil'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando test del nuevo retriever...")
    print()
    
    # Test 1: Nuevo retriever
    test_new_retriever()
    
    # Test 2: Búsqueda directa
    test_direct_similarity()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Si el nuevo retriever funciona mejor, el problema era el tipo de búsqueda.")
    print("Si sigue sin funcionar, puede ser un problema de embeddings.")

if __name__ == "__main__":
    main()
