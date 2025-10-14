#!/usr/bin/env python3
"""
Script para verificar los fragmentos específicos del Excel
"""

import os
import sys

def check_excel_fragments():
    """Verificar los fragmentos específicos del Excel"""
    print("🔍 VERIFICANDO FRAGMENTOS DEL EXCEL")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import load_collection
        
        # Cargar colección
        vectordb = load_collection("sample_documents")
        
        # Buscar todos los fragmentos que contienen información del Excel
        print("📊 Buscando fragmentos del Excel...")
        excel_docs = vectordb.similarity_search("Excel", k=20)
        
        print(f"📄 Fragmentos del Excel encontrados: {len(excel_docs)}")
        print()
        
        for i, doc in enumerate(excel_docs):
            source = doc.metadata.get('source', 'Unknown')
            if 'Inventario_Sostenible.xlsx' in source:
                print(f"📄 Fragmento {i+1}:")
                print(f"  Fuente: {os.path.basename(source)}")
                print(f"  Tipo: {doc.metadata.get('file_type', 'Unknown')}")
                print(f"  Contenido: {doc.page_content}")
                print()
                
                # Verificar si contiene "Cargador Solar Portátil"
                if "Cargador Solar Portátil" in doc.page_content:
                    print("  ✅ ¡Contiene 'Cargador Solar Portátil'!")
                else:
                    print("  ❌ No contiene 'Cargador Solar Portátil'")
                print()
        
        # Buscar específicamente "Cargador Solar Portátil"
        print("🔍 Buscando específicamente 'Cargador Solar Portátil'...")
        cargador_docs = vectordb.similarity_search("Cargador Solar Portátil", k=10)
        
        print(f"📄 Fragmentos con 'Cargador Solar Portátil': {len(cargador_docs)}")
        print()
        
        for i, doc in enumerate(cargador_docs):
            source = doc.metadata.get('source', 'Unknown')
            print(f"📄 Fragmento {i+1}:")
            print(f"  Fuente: {os.path.basename(source)}")
            print(f"  Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"  Contenido: {doc.page_content}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_search():
    """Probar búsqueda directa en el texto del Excel"""
    print("\n" + "=" * 60)
    print("🔍 BÚSQUEDA DIRECTA EN TEXTO DEL EXCEL")
    print("=" * 60)
    print()
    
    try:
        import pandas as pd
        
        # Cargar Excel
        df = pd.read_excel('./static/sample_documents/Inventario_Sostenible.xlsx')
        
        # Convertir a texto como lo hace el sistema
        text_content = "Columnas: " + ", ".join(df.columns.tolist()) + "\n\n"
        
        for index, row in df.iterrows():
            row_text = f"Fila {index + 1}: "
            for col in df.columns:
                if pd.notna(row[col]):
                    row_text += f"{col}: {row[col]}, "
            text_content += row_text.rstrip(", ") + "\n"
        
        print("📝 Texto completo del Excel:")
        print(text_content)
        print()
        
        # Buscar "Cargador Solar Portátil" en el texto
        if "Cargador Solar Portátil" in text_content:
            print("✅ 'Cargador Solar Portátil' encontrado en el texto completo")
            
            # Encontrar la línea específica
            lines = text_content.split('\n')
            for i, line in enumerate(lines):
                if "Cargador Solar Portátil" in line:
                    print(f"📄 Línea {i+1}: {line}")
                    break
        else:
            print("❌ 'Cargador Solar Portátil' no encontrado en el texto completo")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando fragmentos del Excel...")
    print()
    
    # Test 1: Verificar fragmentos en la colección
    check_excel_fragments()
    
    # Test 2: Búsqueda directa en el texto
    test_direct_search()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Si 'Cargador Solar Portátil' está en el texto completo pero no en los fragmentos,")
    print("el problema está en cómo se están dividiendo los documentos.")

if __name__ == "__main__":
    main()
