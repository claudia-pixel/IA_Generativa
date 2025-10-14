#!/usr/bin/env python3
"""
Script para recrear la colección vectorial desde cero
"""

import os
import sys
import shutil

def recreate_vector_collection():
    """Recrear la colección vectorial desde cero"""
    print("🔨 RECREANDO COLECCIÓN VECTORIAL")
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
        
        # 2. Cargar documentos
        print("\n📚 Cargando documentos...")
        from utils.vector_functions import load_sample_documents
        documents, collection_name = load_sample_documents()
        
        if not documents:
            print("❌ No se pudieron cargar los documentos")
            return False
        
        print(f"✅ Cargados {len(documents)} documentos")
        
        # 3. Crear nueva colección
        print("\n🔨 Creando nueva colección...")
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings
        from langchain_text_splitters import CharacterTextSplitter
        from langchain_community.vectorstores.utils import filter_complex_metadata
        
        # Configurar embeddings
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY no configurada")
            return False
        
        embeddings = OpenAIEmbeddings(api_key=api_key)
        print("✅ Embeddings configurados")
        
        # Configurar splitter
        text_splitter = CharacterTextSplitter(
            chunk_size=500,  # Fragmentos más pequeños
            chunk_overlap=50,  # Más superposición
            length_function=len,
            separator="\n"
        )
        
        # Dividir documentos
        texts = text_splitter.split_documents(documents)
        texts = filter_complex_metadata(texts)
        
        print(f"✅ Documentos divididos en {len(texts)} fragmentos")
        
        # Mostrar algunos fragmentos
        print("\n📄 Primeros 3 fragmentos:")
        for i, text in enumerate(texts[:3]):
            print(f"  Fragmento {i+1}:")
            print(f"    Fuente: {text.metadata.get('source', 'Unknown')}")
            print(f"    Contenido: {text.page_content[:200]}...")
            print()
        
        # Crear colección
        print("🔨 Creando colección vectorial...")
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_name="sample_documents",
        )
        
        print("✅ Colección vectorial creada")
        
        # 4. Probar la nueva colección
        print("\n🔍 Probando nueva colección...")
        
        # Probar búsqueda directa
        query = "Cargador Solar Portátil"
        docs = vectordb.similarity_search(query, k=5)
        
        print(f"📊 Documentos encontrados para '{query}': {len(docs)}")
        
        for i, doc in enumerate(docs):
            print(f"\n  📄 Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            
            if "Cargador Solar Portátil" in doc.page_content:
                print("    ✅ ¡Contiene 'Cargador Solar Portátil'!")
            else:
                print("    ❌ No contiene 'Cargador Solar Portátil'")
        
        # 5. Probar retriever
        print("\n🔍 Probando retriever...")
        retriever = vectordb.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        docs = retriever.get_relevant_documents(query)
        print(f"📊 Retriever encontró {len(docs)} documentos")
        
        for i, doc in enumerate(docs[:2]):
            print(f"  Documento {i+1}: {doc.page_content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recreando colección: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_final_rag():
    """Probar el RAG final"""
    print("\n" + "=" * 60)
    print("🚀 PROBANDO RAG FINAL")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        # Crear retriever
        retriever = get_combined_retriever()
        
        # Consultas de prueba
        test_queries = [
            "Cargador Solar Portátil",
            "¿Cuánto cuesta el Cargador Solar Portátil?",
            "lámpara solar",
            "productos de electrónica"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Consulta: {query}")
            print("-" * 40)
            
            docs = retriever.get_relevant_documents(query)
            print(f"📊 Documentos encontrados: {len(docs)}")
            
            # Verificar si alguno contiene información del inventario
            has_inventory = False
            for doc in docs:
                if "Cargador Solar Portátil" in doc.page_content:
                    print("✅ ¡Encontró información sobre el Cargador Solar Portátil!")
                    print(f"   Contenido: {doc.page_content[:200]}...")
                    has_inventory = True
                    break
            
            if not has_inventory:
                print("❌ No encontró información sobre el Cargador Solar Portátil")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test final: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando recreación de colección vectorial...")
    print()
    
    # Recrear colección
    if recreate_vector_collection():
        print("\n✅ Colección recreada exitosamente")
        
        # Probar RAG final
        test_final_rag()
    else:
        print("\n❌ Error recreando colección")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    print("Si la recreación funciona, el problema era la configuración anterior.")
    print("Si sigue sin funcionar, puede ser un problema de embeddings o API key.")

if __name__ == "__main__":
    main()
