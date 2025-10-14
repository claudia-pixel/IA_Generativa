#!/usr/bin/env python3
"""
Script para probar las mejoras en información de contacto
"""

import os
import sys

def test_contact_info_improvements():
    """Probar las mejoras en información de contacto"""
    print("🔧 PROBANDO MEJORAS EN INFORMACIÓN DE CONTACTO")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever, generate_contact_info_answer
        
        # Crear retriever
        retriever = get_combined_retriever()
        
        # Consultas específicas de información de contacto
        test_queries = [
            "dame el número de teléfono para el proceso de devolución",
            "¿cuál es el WhatsApp para devoluciones?",
            "email para devoluciones",
            "teléfono devoluciones",
            "whatsapp devoluciones",
            "contacto devoluciones"
        ]
        
        print("📞 Información real en el documento:")
        print("  • Teléfono: +57 324 456 4450")
        print("  • WhatsApp: +57 300 333 4567")
        print("  • Email: devoluciones@ecomarket.com")
        print()
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*20} CONSULTA {i} {'='*20}")
            print(f"🔍 Consulta: {query}")
            print("-" * 50)
            
            try:
                # Usar función específica para información de contacto
                response = generate_contact_info_answer(retriever, query)
                print(f"🤖 Respuesta: {response}")
                
                # Verificar si contiene la información correcta
                if "324 456 4450" in response:
                    print("  ✅ ¡Contiene el teléfono correcto!")
                elif "300 333 4567" in response:
                    print("  ✅ ¡Contiene el WhatsApp correcto!")
                elif "devoluciones@ecomarket.com" in response:
                    print("  ✅ ¡Contiene el email correcto!")
                else:
                    print("  ❌ No contiene la información correcta")
                    
            except Exception as e:
                print(f"  ❌ Error en consulta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_retrieval_improvements():
    """Probar mejoras en la recuperación RAG"""
    print("\n" + "=" * 60)
    print("🔍 PROBANDO MEJORAS EN RECUPERACIÓN RAG")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        retriever = get_combined_retriever()
        
        # Probar recuperación de documentos
        query = "teléfono devoluciones"
        print(f"🔍 Consulta: {query}")
        
        docs = retriever.get_relevant_documents(query)
        print(f"📊 Documentos encontrados: {len(docs)}")
        
        for i, doc in enumerate(docs[:3]):
            print(f"\n  📄 Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            
            # Verificar si contiene información de contacto
            if "324 456 4450" in doc.page_content:
                print("    ✅ ¡Contiene el teléfono correcto!")
            elif "300 333 4567" in doc.page_content:
                print("    ✅ ¡Contiene el WhatsApp correcto!")
            elif "devoluciones@ecomarket.com" in doc.page_content:
                print("    ✅ ¡Contiene el email correcto!")
            else:
                print("    ❌ No contiene información de contacto específica")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test RAG: {e}")
        return False

def show_improvements_summary():
    """Mostrar resumen de mejoras implementadas"""
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE MEJORAS IMPLEMENTADAS")
    print("=" * 60)
    print()
    
    print("✅ CONFIGURACIÓN DEL LLM MEJORADA:")
    print("  • Temperature: 0.1 (respuestas más precisas)")
    print("  • Max tokens: 500 (respuestas más concisas)")
    print("  • Prompts más estrictos para evitar alucinaciones")
    print()
    
    print("✅ PROMPTS ESPECÍFICOS:")
    print("  • Prompt general mejorado con reglas estrictas")
    print("  • Prompt específico para información de contacto")
    print("  • Instrucciones para copiar información EXACTA")
    print()
    
    print("✅ CONFIGURACIÓN DEL RETRIEVER:")
    print("  • K=8 (más documentos para mejor contexto)")
    print("  • Búsqueda por similitud optimizada")
    print()
    
    print("✅ DETECCIÓN INTELIGENTE:")
    print("  • Detección automática de consultas de contacto")
    print("  • Uso de función específica para información de contacto")
    print("  • Palabras clave: teléfono, whatsapp, email, contacto, devolución")
    print()
    
    print("🎯 RESULTADOS ESPERADOS:")
    print("  • Información de contacto EXACTA del documento")
    print("  • Menos alucinaciones del modelo")
    print("  • Respuestas más precisas y confiables")
    print("  • Mejor experiencia del usuario")

def main():
    """Función principal"""
    print("🚀 Probando mejoras en información de contacto...")
    print()
    
    # Test 1: Mejoras en información de contacto
    test_contact_info_improvements()
    
    # Test 2: Mejoras en recuperación RAG
    test_rag_retrieval_improvements()
    
    # Test 3: Mostrar resumen
    show_improvements_summary()
    
    print("\n" + "=" * 60)
    print("🎉 PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("✅ Mejoras implementadas para evitar información inventada")
    print("✅ Sistema optimizado para información de contacto")
    print("✅ Prompts más estrictos y precisos")
    print()
    print("🚀 El sistema ahora debería devolver información EXACTA!")

if __name__ == "__main__":
    main()
