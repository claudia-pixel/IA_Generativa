#!/usr/bin/env python3
"""
Script de prueba para verificar que los documentos de muestra se cargan correctamente.
"""

import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.vector_functions import test_sample_documents, initialize_sample_collection

def main():
    print("=" * 60)
    print("🧪 PRUEBA DE CARGA DE DOCUMENTOS DE MUESTRA")
    print("=" * 60)
    print()
    
    # Test 1: Initialize sample collection
    print("1️⃣ Inicializando colección de documentos de muestra...")
    success = initialize_sample_collection()
    
    if success:
        print("✅ Inicialización exitosa")
    else:
        print("❌ Error en la inicialización")
        return
    
    print()
    
    # Test 2: Test document loading and querying
    print("2️⃣ Probando carga y consulta de documentos...")
    test_success = test_sample_documents()
    
    if test_success:
        print("✅ Prueba de documentos exitosa")
    else:
        print("❌ Error en la prueba de documentos")
        return
    
    print()
    print("=" * 60)
    print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("=" * 60)
    print()
    print("Los documentos de muestra están listos para usar en la aplicación.")

if __name__ == "__main__":
    main()
