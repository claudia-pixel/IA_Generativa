#!/usr/bin/env python3
"""
Script para probar el RAG con umbral de similitud más bajo
"""

import os
import sys

def test_with_lower_threshold():
    """Probar el RAG con umbral más bajo"""
    print("🔍 PROBANDO RAG CON UMBRAL MÁS BAJO")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Configurar API key si no está configurada
        if not os.environ.get('OPENAI_API_KEY'):
            print("⚠️  OPENAI_API_KEY no configurada")
            return False
        
        print("✅ API key configurada")
        
        # Crear retriever con umbral más bajo
        print("🔧 Creando retriever con umbral 0.3...")
        retriever = get_combined_retriever(score_threshold=0.3)
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
                    for j, doc in enumerate(docs[:2]):  # Mostrar máximo 2
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

def test_different_thresholds():
    """Probar diferentes umbrales de similitud"""
    print("\n" + "=" * 60)
    print("🎯 PROBANDO DIFERENTES UMBRALES DE SIMILITUD")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        thresholds = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        query = "Cargador Solar Portátil"
        
        for threshold in thresholds:
            print(f"\n🔍 Umbral: {threshold}")
            print("-" * 30)
            
            try:
                retriever = get_combined_retriever(score_threshold=threshold)
                docs = retriever.get_relevant_documents(query)
                
                print(f"  📊 Documentos encontrados: {len(docs)}")
                
                # Verificar si alguno contiene información del inventario
                has_inventory = False
                for doc in docs:
                    if 'inventario' in doc.page_content.lower() or 'excel' in doc.metadata.get('file_type', ''):
                        has_inventory = True
                        break
                
                if has_inventory:
                    print("  ✅ ¡Encontró información del inventario!")
                else:
                    print("  ❌ No encontró información del inventario")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de umbrales: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando test con umbral más bajo...")
    print()
    
    # Test 1: Umbral más bajo
    test_with_lower_threshold()
    
    # Test 2: Diferentes umbrales
    test_different_thresholds()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Si con umbral 0.3 funciona mejor, el problema era el umbral muy alto.")
    print("Si sigue sin funcionar, puede ser un problema de embeddings o configuración.")

if __name__ == "__main__":
    main()
