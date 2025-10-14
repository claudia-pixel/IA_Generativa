#!/usr/bin/env python3
"""
Script para verificar el contenido del Excel
"""

import pandas as pd

def check_excel_content():
    """Verificar el contenido del archivo Excel"""
    print("📊 VERIFICANDO CONTENIDO DEL EXCEL")
    print("=" * 50)
    
    try:
        df = pd.read_excel('./static/sample_documents/Inventario_Sostenible.xlsx')
        
        print(f"📋 Total de productos: {len(df)}")
        print()
        
        print("📄 LISTA COMPLETA DE PRODUCTOS:")
        print("-" * 50)
        for i, row in df.iterrows():
            nombre = row['Nombre del Producto']
            precio = row['Precio Unitario ($)']
            categoria = row['Categoría']
            stock = row['Cantidad en Stock']
            print(f"{i+1:2d}. {nombre}")
            print(f"    Categoría: {categoria}")
            print(f"    Precio: ${precio}")
            print(f"    Stock: {stock}")
            print()
        
        print("🔍 BUSCANDO PRODUCTOS CON 'CARGADOR' O 'SOLAR':")
        print("-" * 50)
        cargadores = df[df['Nombre del Producto'].str.contains('cargador|solar', case=False, na=False)]
        
        if len(cargadores) > 0:
            print(f"✅ Encontrados {len(cargadores)} productos:")
            for i, row in cargadores.iterrows():
                print(f"  - {row['Nombre del Producto']} - ${row['Precio Unitario ($)']}")
        else:
            print("❌ No se encontraron productos con 'cargador' o 'solar'")
            print()
            print("💡 PRODUCTOS DISPONIBLES:")
            for i, row in df.iterrows():
                print(f"  - {row['Nombre del Producto']}")
        
        print()
        print("🔍 BUSCANDO PRODUCTOS CON 'LED' O 'LÁMPARA':")
        print("-" * 50)
        leds = df[df['Nombre del Producto'].str.contains('led|lámpara|lamp', case=False, na=False)]
        
        if len(leds) > 0:
            print(f"✅ Encontrados {len(leds)} productos:")
            for i, row in leds.iterrows():
                print(f"  - {row['Nombre del Producto']} - ${row['Precio Unitario ($)']}")
        else:
            print("❌ No se encontraron productos con 'LED' o 'lámpara'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return False

if __name__ == "__main__":
    check_excel_content()
