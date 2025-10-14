#!/usr/bin/env python3
"""
Script para probar consultas específicas del RAG
"""

import os
import sys

def test_specific_queries():
    """Probar consultas específicas del inventario"""
    print("🔍 PROBANDO CONSULTAS ESPECÍFICAS DEL RAG")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Configurar API key si no está configurada
        if not os.environ.get('OPENAI_API_KEY'):
            print("⚠️  OPENAI_API_KEY no configurada")
            print("Configurando API key de prueba...")
            # Aquí deberías poner tu API key real
            print("Por favor, configura tu API key: export OPENAI_API_KEY='tu_api_key'")
            return False
        
        print("✅ API key configurada")
        
        # Crear retriever
        print("🔧 Creando retriever...")
        retriever = get_combined_retriever()
        print("✅ Retriever creado")
        
        # Consultas específicas para probar
        test_queries = [
            "Cargador Solar Portátil",
            "cargador solar",
            "¿Cuánto cuesta el Cargador Solar Portátil?",
            "¿Cuál es el precio del Cargador Solar Portátil?",
            "productos de electrónica",
            "cargadores",
            "lámpara solar",
            "¿Qué productos hay en la categoría Electrónica?",
            "inventario de productos",
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

def test_direct_excel_query():
    """Probar consulta directa al contenido del Excel"""
    print("\n" + "=" * 60)
    print("📊 PROBANDO CONSULTA DIRECTA AL EXCEL")
    print("=" * 60)
    print()
    
    try:
        import pandas as pd
        
        # Cargar Excel
        df = pd.read_excel('./static/sample_documents/Inventario_Sostenible.xlsx')
        
        # Buscar cargador solar
        cargador = df[df['Nombre del Producto'].str.contains('Cargador Solar Portátil', case=False, na=False)]
        
        if len(cargador) > 0:
            print("✅ Cargador Solar Portátil encontrado en Excel:")
            row = cargador.iloc[0]
            print(f"  📦 Producto: {row['Nombre del Producto']}")
            print(f"  💰 Precio: ${row['Precio Unitario ($)']}")
            print(f"  📂 Categoría: {row['Categoría']}")
            print(f"  📊 Stock: {row['Cantidad en Stock']}")
            print(f"  📅 Fecha: {row['Fecha de Ingreso']}")
        else:
            print("❌ Cargador Solar Portátil no encontrado en Excel")
        
        # Crear texto para RAG
        print("\n📝 Texto generado para RAG:")
        text_content = "Columnas: " + ", ".join(df.columns.tolist()) + "\n\n"
        
        for index, row in df.iterrows():
            row_text = f"Fila {index + 1}: "
            for col in df.columns:
                if pd.notna(row[col]):
                    row_text += f"{col}: {row[col]}, "
            text_content += row_text.rstrip(", ") + "\n"
        
        # Buscar en el texto
        if "Cargador Solar Portátil" in text_content:
            print("✅ 'Cargador Solar Portátil' encontrado en texto para RAG")
            
            # Mostrar la línea específica
            lines = text_content.split('\n')
            for line in lines:
                if "Cargador Solar Portátil" in line:
                    print(f"  📄 Línea: {line}")
                    break
        else:
            print("❌ 'Cargador Solar Portátil' no encontrado en texto para RAG")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test directo: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando test de consultas específicas...")
    print()
    
    # Test 1: Consulta directa al Excel
    test_direct_excel_query()
    
    # Test 2: Consultas RAG
    test_specific_queries()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Si el Excel contiene el producto pero el RAG no lo encuentra,")
    print("el problema puede estar en:")
    print("1. La configuración del retriever")
    print("2. El umbral de similitud (score_threshold)")
    print("3. La forma en que se procesan los embeddings")

if __name__ == "__main__":
    main()
