#!/usr/bin/env python3
"""
Script para diagnosticar problemas del sistema RAG
"""

import os
import sys
import pandas as pd
from langchain_core.documents import Document

def test_excel_loading():
    """Probar la carga específica del archivo Excel"""
    print("=" * 60)
    print("📊 DIAGNÓSTICO DE CARGA DE EXCEL")
    print("=" * 60)
    print()
    
    excel_file = "./static/sample_documents/Inventario_Sostenible.xlsx"
    
    if not os.path.exists(excel_file):
        print(f"❌ Archivo Excel no encontrado: {excel_file}")
        return False
    
    print(f"✅ Archivo Excel encontrado: {excel_file}")
    
    try:
        # Cargar con pandas
        df = pd.read_excel(excel_file)
        print(f"📊 Filas en Excel: {len(df)}")
        print(f"📋 Columnas: {list(df.columns)}")
        print()
        
        # Mostrar primeras filas
        print("📄 Primeras 3 filas del Excel:")
        for i in range(min(3, len(df))):
            row = df.iloc[i]
            print(f"  Fila {i+1}:")
            for col in df.columns:
                if pd.notna(row[col]):
                    print(f"    {col}: {row[col]}")
            print()
        
        # Convertir a texto para RAG
        text_content = ""
        text_content += "Columnas: " + ", ".join(df.columns.tolist()) + "\n\n"
        
        for index, row in df.iterrows():
            row_text = f"Fila {index + 1}: "
            for col in df.columns:
                if pd.notna(row[col]):
                    row_text += f"{col}: {row[col]}, "
            text_content += row_text.rstrip(", ") + "\n"
        
        print("📝 Contenido convertido a texto:")
        print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando Excel: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vector_collection_creation():
    """Probar la creación de la colección vectorial"""
    print("\n" + "=" * 60)
    print("🔨 DIAGNÓSTICO DE COLECCIÓN VECTORIAL")
    print("=" * 60)
    print()
    
    try:
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings
        from langchain_text_splitters import CharacterTextSplitter
        from langchain_community.vectorstores.utils import filter_complex_metadata
        import environ
        
        # Configurar entorno
        env = environ.Env()
        environ.Env.read_env()
        
        # Verificar API key
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY no configurada")
            print("Configura la variable de entorno: export OPENAI_API_KEY='tu_api_key'")
            return False
        
        print(f"✅ API key configurada: {api_key[:10]}...")
        
        # Cargar documentos
        print("📚 Cargando documentos de muestra...")
        from utils.vector_functions import load_sample_documents
        documents, collection_name = load_sample_documents()
        
        if not documents:
            print("❌ No se pudieron cargar los documentos")
            return False
        
        print(f"✅ Cargados {len(documents)} documentos")
        
        # Mostrar información de cada documento
        for i, doc in enumerate(documents):
            print(f"  Documento {i+1}:")
            print(f"    Fuente: {doc.metadata.get('source', 'Unknown')}")
            print(f"    Tipo: {doc.metadata.get('file_type', 'Unknown')}")
            print(f"    Contenido: {doc.page_content[:200]}...")
            print()
        
        # Crear embeddings y splitter
        print("🔧 Configurando embeddings y splitter...")
        embeddings = OpenAIEmbeddings(api_key=api_key)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        
        # Dividir documentos
        texts = text_splitter.split_documents(documents)
        texts = filter_complex_metadata(texts)
        
        print(f"✅ Documentos divididos en {len(texts)} fragmentos")
        
        # Mostrar algunos fragmentos
        print("📄 Primeros 2 fragmentos:")
        for i, text in enumerate(texts[:2]):
            print(f"  Fragmento {i+1}: {text.page_content[:200]}...")
            print(f"    Metadatos: {text.metadata}")
            print()
        
        # Crear colección
        print("🔨 Creando colección vectorial...")
        persist_directory = "./static/persist"
        os.makedirs(persist_directory, exist_ok=True)
        
        # Limpiar colección existente si existe
        collection_path = os.path.join(persist_directory, "sample_documents")
        if os.path.exists(collection_path):
            import shutil
            shutil.rmtree(collection_path)
            print("🗑️  Colección anterior eliminada")
        
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="sample_documents",
        )
        
        print("✅ Colección vectorial creada exitosamente")
        
        # Probar retriever
        print("🔍 Probando retriever...")
        retriever = vectordb.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.6},
        )
        
        # Probar consultas específicas
        test_queries = [
            "¿Cuál es el costo de un cargador solar portátil?",
            "¿Qué productos hay en el inventario?",
            "¿Cuánto cuesta la lámpara LED?",
            "¿Cuál es la política de devoluciones?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Consulta: {query}")
            try:
                docs = retriever.get_relevant_documents(query)
                print(f"  📊 Documentos relevantes: {len(docs)}")
                
                for i, doc in enumerate(docs[:2]):  # Mostrar máximo 2
                    print(f"    Documento {i+1}:")
                    print(f"      Contenido: {doc.page_content[:200]}...")
                    print(f"      Metadatos: {doc.metadata}")
                    print(f"      Score: {getattr(doc, 'score', 'N/A')}")
                
                if len(docs) == 0:
                    print("    ⚠️  No se encontraron documentos relevantes")
                    
            except Exception as e:
                print(f"    ❌ Error en consulta: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de colección: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_combined_retriever():
    """Probar el retriever combinado"""
    print("\n" + "=" * 60)
    print("🔍 DIAGNÓSTICO DE RETRIEVER COMBINADO")
    print("=" * 60)
    print()
    
    try:
        from utils.vector_functions import get_combined_retriever
        
        print("🔧 Creando retriever combinado...")
        retriever = get_combined_retriever()
        print("✅ Retriever combinado creado")
        
        # Probar consultas
        test_queries = [
            "¿Cuál es el costo de un cargador solar portátil?",
            "¿Qué productos hay en el inventario?",
            "¿Cuál es la política de devoluciones?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Consulta: {query}")
            try:
                docs = retriever.get_relevant_documents(query)
                print(f"  📊 Documentos relevantes: {len(docs)}")
                
                for i, doc in enumerate(docs[:2]):
                    print(f"    Documento {i+1}: {doc.page_content[:200]}...")
                
                if len(docs) == 0:
                    print("    ⚠️  No se encontraron documentos relevantes")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de retriever combinado: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando diagnóstico del sistema RAG...")
    print()
    
    # Verificar API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY no configurada")
        print("Para probar el RAG, configura la variable de entorno:")
        print("export OPENAI_API_KEY='tu_api_key_aqui'")
        print()
        print("Continuando con diagnóstico básico...")
        print()
    
    # Tests
    tests = [
        ("Carga de Excel", test_excel_loading),
        ("Colección Vectorial", test_vector_collection_creation),
        ("Retriever Combinado", test_combined_retriever)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{'='*20} {name.upper()} {'='*20}")
        try:
            result = test_func()
            results.append((name, result))
            print(f"Resultado: {'✅ ÉXITO' if result else '❌ FALLO'}")
        except Exception as e:
            print(f"❌ Error en test: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO RAG")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if result:
            success_count += 1
    
    total_count = len(results)
    print(f"\n📈 Éxito: {success_count}/{total_count} tests")
    
    if success_count == total_count:
        print("\n🎉 ¡Sistema RAG funcionando correctamente!")
    else:
        print("\n⚠️  El sistema RAG tiene problemas que necesitan ser resueltos.")

if __name__ == "__main__":
    main()
