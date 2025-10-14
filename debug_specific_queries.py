#!/usr/bin/env python3
"""
Script para diagnosticar consultas específicas y verificar si el RAG encuentra la información correcta
"""

import os
import sys

def test_specific_queries():
    """Probar consultas específicas sobre información de contacto"""
    print("🔍 DIAGNOSTICANDO CONSULTAS ESPECÍFICAS")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Crear retriever
        retriever = get_combined_retriever()
        
        # Consultas específicas sobre información de contacto
        test_queries = [
            "número de teléfono para devoluciones",
            "teléfono devoluciones",
            "WhatsApp devoluciones",
            "email devoluciones",
            "devoluciones@ecomarket.com",
            "324 456 4450",
            "300 333 4567",
            "proceso de devolución contacto",
            "servicio de atención al cliente devoluciones"
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
                        print(f"    Contenido: {doc.page_content}")
                        
                        # Verificar si contiene información de contacto real
                        content = doc.page_content
                        if "324 456 4450" in content:
                            print("    ✅ ¡Contiene el teléfono correcto!")
                        elif "300 333 4567" in content:
                            print("    ✅ ¡Contiene el WhatsApp correcto!")
                        elif "devoluciones@ecomarket.com" in content:
                            print("    ✅ ¡Contiene el email correcto!")
                        else:
                            print("    ❌ No contiene información de contacto específica")
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

def test_document_content():
    """Verificar el contenido real del documento"""
    print("\n" + "=" * 60)
    print("📄 VERIFICANDO CONTENIDO REAL DEL DOCUMENTO")
    print("=" * 60)
    print()
    
    try:
        # Leer el archivo directamente
        with open("./static/sample_documents/politica_devoluciones.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        print("📄 Contenido del archivo politica_devoluciones.txt:")
        print("-" * 50)
        
        # Buscar líneas con información de contacto
        lines = content.split('\n')
        contact_lines = []
        
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['teléfono', 'whatsapp', 'email', 'devoluciones@']):
                contact_lines.append(f"Línea {i+1}: {line}")
        
        print("📞 Información de contacto encontrada:")
        for line in contact_lines:
            print(f"  {line}")
        
        # Verificar números específicos
        print("\n🔍 Verificando números específicos:")
        if "324 456 4450" in content:
            print("  ✅ Teléfono 324 456 4450 encontrado")
        else:
            print("  ❌ Teléfono 324 456 4450 NO encontrado")
            
        if "300 333 4567" in content:
            print("  ✅ WhatsApp 300 333 4567 encontrado")
        else:
            print("  ❌ WhatsApp 300 333 4567 NO encontrado")
            
        if "devoluciones@ecomarket.com" in content:
            print("  ✅ Email devoluciones@ecomarket.com encontrado")
        else:
            print("  ❌ Email devoluciones@ecomarket.com NO encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo documento: {e}")
        return False

def test_rag_retrieval():
    """Probar específicamente la recuperación RAG"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO RECUPERACIÓN RAG ESPECÍFICA")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_collection
        
        # Cargar colección directamente
        vectordb = load_collection("sample_documents")
        
        # Búsqueda específica
        query = "teléfono devoluciones"
        print(f"🔍 Búsqueda: {query}")
        
        # Usar similarity_search directamente
        docs = vectordb.similarity_search(query, k=5)
        print(f"📊 Documentos encontrados: {len(docs)}")
        
        for i, doc in enumerate(docs):
            print(f"\n  📄 Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Contenido: {doc.page_content}")
            
            # Verificar si contiene el teléfono correcto
            if "324 456 4450" in doc.page_content:
                print("    ✅ ¡Contiene el teléfono correcto!")
            else:
                print("    ❌ No contiene el teléfono correcto")
        
        # Búsqueda con score
        print(f"\n🔍 Búsqueda con scores: {query}")
        docs_with_scores = vectordb.similarity_search_with_score(query, k=5)
        
        for i, (doc, score) in enumerate(docs_with_scores):
            print(f"\n  📄 Documento {i+1} (score: {score:.3f}):")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            
            if "324 456 4450" in doc.page_content:
                print("    ✅ ¡Contiene el teléfono correcto!")
            else:
                print("    ❌ No contiene el teléfono correcto")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test RAG: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Diagnosticando problema de información inventada...")
    print()
    
    # Test 1: Verificar contenido real
    test_document_content()
    
    # Test 2: Probar recuperación RAG
    test_rag_retrieval()
    
    # Test 3: Probar consultas específicas
    test_specific_queries()
    
    print("\n" + "=" * 60)
    print("📊 DIAGNÓSTICO COMPLETADO")
    print("=" * 60)
    print("Si el RAG no encuentra la información correcta,")
    print("el problema puede estar en:")
    print("1. Fragmentación incorrecta del documento")
    print("2. Embeddings no capturan bien la información específica")
    print("3. Configuración del retriever")
    print("4. El modelo de lenguaje genera información inventada")

if __name__ == "__main__":
    main()
