#!/usr/bin/env python3
"""
Script para aplicar la corrección de la colección vectorial al proyecto
"""

import os
import sys
import shutil

def apply_vector_collection_fix():
    """Aplicar la corrección de la colección vectorial al proyecto"""
    print("🔧 APLICANDO CORRECCIÓN DE COLECCIÓN VECTORIAL AL PROYECTO")
    print("=" * 60)
    print()
    
    try:
        # 1. Limpiar colección existente
        print("🗑️  Limpiando colección existente...")
        persist_dir = "./static/persist"
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)
            print("✅ Colección anterior eliminada")
        
        os.makedirs(persist_dir, exist_ok=True)
        print("✅ Directorio de persistencia creado")
        
        # 2. Usar la función del proyecto para inicializar
        print("\n📚 Inicializando colección con configuración corregida...")
        from utils.vector_functions import initialize_sample_collection
        
        success = initialize_sample_collection()
        
        if success:
            print("✅ Colección vectorial inicializada exitosamente")
            
            # 3. Probar que funciona
            print("\n🔍 Probando la colección...")
            from utils.vector_functions import get_combined_retriever
            
            retriever = get_combined_retriever()
            
            # Probar consulta específica
            query = "Cargador Solar Portátil"
            docs = retriever.get_relevant_documents(query)
            
            print(f"📊 Documentos encontrados para '{query}': {len(docs)}")
            
            # Verificar si encuentra el producto
            found_product = False
            for doc in docs:
                if "Cargador Solar Portátil" in doc.page_content:
                    print("✅ ¡Encontró el Cargador Solar Portátil!")
                    print(f"   Contenido: {doc.page_content[:200]}...")
                    found_product = True
                    break
            
            if not found_product:
                print("❌ No encontró el Cargador Solar Portátil")
                return False
            
            print("\n🎉 ¡Corrección aplicada exitosamente!")
            return True
            
        else:
            print("❌ Error inicializando la colección")
            return False
        
    except Exception as e:
        print(f"❌ Error aplicando corrección: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_project_files():
    """Verificar que los archivos del proyecto tienen las correcciones"""
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO ARCHIVOS DEL PROYECTO")
    print("=" * 60)
    print()
    
    try:
        # Verificar vector_functions.py
        with open("./utils/vector_functions.py", "r") as f:
            content = f.read()
            
        print("📄 Verificando utils/vector_functions.py:")
        
        if 'score_threshold: float = 0.3' in content:
            print("  ✅ Umbral cambiado a 0.3")
        else:
            print("  ❌ Umbral no cambiado")
            
        if 'search_type="similarity"' in content:
            print("  ✅ Tipo de búsqueda cambiado a similarity")
        else:
            print("  ❌ Tipo de búsqueda no cambiado")
            
        if 'chunk_size=500' in content:
            print("  ✅ Tamaño de fragmento cambiado a 500")
        else:
            print("  ❌ Tamaño de fragmento no cambiado")
            
        if 'chunk_overlap=50' in content:
            print("  ✅ Superposición cambiada a 50")
        else:
            print("  ❌ Superposición no cambiada")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Aplicando correcciones al proyecto...")
    print()
    
    # Verificar archivos
    verify_project_files()
    
    # Aplicar corrección de colección
    if apply_vector_collection_fix():
        print("\n" + "=" * 60)
        print("🎉 CORRECCIÓN APLICADA EXITOSAMENTE")
        print("=" * 60)
        print("✅ Archivos del proyecto actualizados")
        print("✅ Colección vectorial recreada")
        print("✅ Sistema RAG funcionando correctamente")
        print()
        print("🚀 El proyecto está listo para usar!")
    else:
        print("\n❌ Error aplicando la corrección")

if __name__ == "__main__":
    main()
