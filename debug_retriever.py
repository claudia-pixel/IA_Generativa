#!/usr/bin/env python3
"""
Script para debuggear el retriever específicamente
"""

import os
import sys

def test_individual_retrievers():
    """Probar los retrievers individuales"""
    print("🔍 PROBANDO RETRIEVERS INDIVIDUALES")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_retriever
        
        # Test 1: Retriever de documentos de muestra
        print("📚 Probando retriever de documentos de muestra...")
        try:
            sample_retriever = load_retriever("sample_documents", score_threshold=0.3)
            print("✅ Retriever de muestra creado")
            
            query = "Cargador Solar Portátil"
            docs = sample_retriever.get_relevant_documents(query)
            print(f"📊 Documentos encontrados: {len(docs)}")
            
            for i, doc in enumerate(docs[:2]):
                print(f"  Documento {i+1}:")
                print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
                print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
                print(f"    Contenido: {doc.page_content[:200]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error con retriever de muestra: {e}")
        
        # Test 2: Retriever de documentos regulares
        print("📚 Probando retriever de documentos regulares...")
        try:
            regular_retriever = load_retriever("ecomarket_kb", score_threshold=0.3)
            print("✅ Retriever regular creado")
            
            query = "Cargador Solar Portátil"
            docs = regular_retriever.get_relevant_documents(query)
            print(f"📊 Documentos encontrados: {len(docs)}")
            
            for i, doc in enumerate(docs[:2]):
                print(f"  Documento {i+1}:")
                print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
                print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
                print(f"    Contenido: {doc.page_content[:200]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error con retriever regular: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test individual: {e}")
        return False

def test_collection_directly():
    """Probar la colección directamente"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO COLECCIÓN DIRECTAMENTE")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_collection
        
        # Cargar colección de muestra
        print("📚 Cargando colección de muestra...")
        vectordb = load_collection("sample_documents")
        print("✅ Colección cargada")
        
        # Verificar contenido
        print("📊 Verificando contenido de la colección...")
        count = vectordb._collection.count()
        print(f"Total de documentos en colección: {count}")
        
        # Probar búsqueda directa
        print("\n🔍 Probando búsqueda directa...")
        query = "Cargador Solar Portátil"
        
        # Usar similarity_search directamente
        docs = vectordb.similarity_search(query, k=5)
        print(f"📊 Documentos encontrados con similarity_search: {len(docs)}")
        
        for i, doc in enumerate(docs[:3]):
            print(f"  Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            print()
        
        # Probar con similarity_search_with_score
        print("\n🔍 Probando búsqueda con scores...")
        docs_with_scores = vectordb.similarity_search_with_score(query, k=5)
        print(f"📊 Documentos encontrados con scores: {len(docs_with_scores)}")
        
        for i, (doc, score) in enumerate(docs_with_scores[:3]):
            print(f"  Documento {i+1} (score: {score:.3f}):")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_different_queries():
    """Probar diferentes tipos de consultas"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO DIFERENTES CONSULTAS")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_collection
        
        vectordb = load_collection("sample_documents")
        
        queries = [
            "Cargador Solar Portátil",
            "cargador solar",
            "solar",
            "cargador",
            "portátil",
            "electrónica",
            "inventario",
            "productos",
            "precio",
            "49.99",
            "Fila 4",
            "Nombre del Producto"
        ]
        
        for query in queries:
            print(f"\n🔍 Consulta: '{query}'")
            print("-" * 40)
            
            try:
                docs = vectordb.similarity_search(query, k=3)
                print(f"  📊 Documentos encontrados: {len(docs)}")
                
                for i, doc in enumerate(docs):
                    source = doc.metadata.get('source', 'Unknown')
                    file_type = doc.metadata.get('file_type', 'Unknown')
                    content = doc.page_content[:100]
                    
                    print(f"    {i+1}. {os.path.basename(source)} ({file_type})")
                    print(f"       {content}...")
                    
                    # Verificar si contiene la consulta
                    if query.lower() in doc.page_content.lower():
                        print(f"       ✅ Contiene '{query}'")
                    else:
                        print(f"       ❌ No contiene '{query}'")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de consultas: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando debug del retriever...")
    print()
    
    # Test 1: Retrievers individuales
    test_individual_retrievers()
    
    # Test 2: Colección directamente
    test_collection_directly()
    
    # Test 3: Diferentes consultas
    test_different_queries()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Este debug nos ayudará a entender por qué el retriever")
    print("no está encontrando los documentos del inventario.")

if __name__ == "__main__":
    main()
