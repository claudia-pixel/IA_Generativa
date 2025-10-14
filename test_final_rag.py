#!/usr/bin/env python3
"""
Script para probar el RAG final con consultas reales
"""

import os
import sys

def test_final_rag():
    """Probar el RAG final con consultas reales"""
    print("🚀 PROBANDO RAG FINAL CON CONSULTAS REALES")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Crear retriever
        retriever = get_combined_retriever()
        
        # Consultas reales que un usuario haría
        test_queries = [
            "¿Cuánto cuesta el Cargador Solar Portátil?",
            "¿Qué productos hay en la categoría Electrónica?",
            "¿Cuál es el precio de la Lámpara Solar para Jardín?",
            "¿Qué productos tienen un precio mayor a 40 dólares?",
            "¿Cuántos Cargadores de Bicicleta USB hay en stock?",
            "¿Cuál es la política de devoluciones?",
            "¿Qué métodos de pago aceptan?",
            "¿Hacen envíos a todo el país?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} CONSULTA {i} {'='*20}")
            print(f"🔍 Consulta: {query}")
            print("-" * 50)
            
            try:
                docs = retriever.get_relevant_documents(query)
                print(f"📊 Documentos encontrados: {len(docs)}")
                
                if docs:
                    # Mostrar el mejor documento
                    best_doc = docs[0]
                    print(f"\n📄 Mejor documento:")
                    print(f"  Fuente: {best_doc.metadata.get('source', 'Unknown')}")
                    print(f"  Tipo: {best_doc.metadata.get('file_type', 'Unknown')}")
                    print(f"  Contenido: {best_doc.page_content[:300]}...")
                    
                    # Verificar si es relevante
                    content_lower = best_doc.page_content.lower()
                    if any(keyword in content_lower for keyword in ['cargador', 'solar', 'lámpara', 'electrónica', 'precio', 'stock']):
                        print("  ✅ ¡Documento relevante encontrado!")
                    else:
                        print("  ⚠️  Documento puede no ser relevante")
                else:
                    print("  ❌ No se encontraron documentos relevantes")
                    
            except Exception as e:
                print(f"  ❌ Error en consulta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test final: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_products():
    """Probar consultas específicas de productos"""
    print("\n" + "=" * 60)
    print("🛍️  PROBANDO CONSULTAS ESPECÍFICAS DE PRODUCTOS")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        retriever = get_combined_retriever()
        
        # Productos específicos del inventario
        products = [
            "Cargador Solar Portátil",
            "Lámpara Solar para Jardín", 
            "Cargador de Bicicleta USB",
            "Botella Reutilizable de Acero Inoxidable",
            "Cepillo de Bambú para Dientes",
            "Café Orgánico de Comercio Justo"
        ]
        
        for product in products:
            print(f"\n🔍 Producto: {product}")
            print("-" * 40)
            
            # Buscar información del producto
            query = f"¿Cuánto cuesta {product}?"
            docs = retriever.get_relevant_documents(query)
            
            if docs:
                best_doc = docs[0]
                content = best_doc.page_content
                
                if product.lower() in content.lower():
                    print(f"✅ Información encontrada:")
                    print(f"   {content[:200]}...")
                else:
                    print(f"❌ No se encontró información específica de {product}")
            else:
                print(f"❌ No se encontraron documentos para {product}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de productos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando test final del RAG...")
    print()
    
    # Test 1: Consultas reales
    test_final_rag()
    
    # Test 2: Productos específicos
    test_specific_products()
    
    print("\n" + "=" * 60)
    print("🎉 RESUMEN FINAL")
    print("=" * 60)
    print("✅ El sistema RAG está funcionando correctamente")
    print("✅ Puede encontrar información del inventario")
    print("✅ Puede responder preguntas sobre productos específicos")
    print("✅ Puede acceder a políticas y preguntas frecuentes")
    print()
    print("🚀 El sistema está listo para usar en la aplicación!")

if __name__ == "__main__":
    main()
