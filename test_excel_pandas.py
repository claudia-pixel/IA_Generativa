#!/usr/bin/env python3
"""
Script de prueba para verificar la carga del archivo Excel con pandas.
"""

import os
import sys
import pandas as pd

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_excel_loading():
    """Test loading the Excel file with pandas"""
    print("=" * 60)
    print("🧪 PRUEBA DE CARGA DE ARCHIVO EXCEL CON PANDAS")
    print("=" * 60)
    print()
    
    excel_file = "./static/sample_documents/Inventario_Sostenible.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Archivo no encontrado: {excel_file}")
        return False
    
    try:
        print(f"📄 Cargando archivo: {excel_file}")
        
        # Load with pandas
        df = pd.read_excel(excel_file)
        
        print(f"✅ Archivo cargado exitosamente")
        print(f"📊 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"📋 Columnas: {list(df.columns)}")
        print()
        
        # Show first few rows
        print("📋 Primeras 5 filas:")
        print(df.head().to_string())
        print()
        
        # Show data types
        print("🔍 Tipos de datos:")
        print(df.dtypes)
        print()
        
        # Check for cargador solar
        print("🔍 Buscando 'Cargador Solar'...")
        cargador_rows = df[df.astype(str).apply(lambda x: x.str.contains('Cargador Solar', case=False, na=False)).any(axis=1)]
        
        if not cargador_rows.empty:
            print("✅ Encontrado 'Cargador Solar':")
            print(cargador_rows.to_string())
        else:
            print("❌ No se encontró 'Cargador Solar'")
            print("📋 Contenido completo del archivo:")
            print(df.to_string())
        
        return True
        
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
