#!/usr/bin/env python3
"""
Script para probar la carga de documentos en la base de datos vectorial
"""

import os
import sys
import pandas as pd
from langchain_core.documents import Document

def load_excel_with_pandas(file_path: str) -> list[Document]:
    """
    Load Excel file using pandas for better reliability.
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to text
        text_content = ""
        
        # Add column headers
        if not df.empty:
            text_content += "Columnas: " + ", ".join(df.columns.tolist()) + "\n\n"
            
            # Add each row as text
            for index, row in df.iterrows():
                row_text = f"Fila {index + 1}: "
                for col in df.columns:
                    if pd.notna(row[col]):  # Only add non-null values
                        row_text += f"{col}: {row[col]}, "
                text_content += row_text.rstrip(", ") + "\n"
        
        # Create document
        document = Document(
            page_content=text_content,
            metadata={
                "source": file_path,
                "file_type": "excel",
                "source_type": "inventory",
                "total_rows": str(len(df)),
                "columns": ", ".join(df.columns.tolist())
            }
        )
        
        return [document]
        
    except Exception as e:
        print(f"Error loading Excel file with pandas: {e}")
        return []

def load_text_file(file_path: str) -> list[Document]:
    """Load a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        document = Document(
            page_content=content,
            metadata={
                "source": file_path,
                "file_type": "text",
                "source_type": "policy" if "politica" in file_path.lower() else "faq"
            }
        )
        
        return [document]
        
    except Exception as e:
        print(f"Error loading text file: {e}")
        return []

def test_document_loading():
    """Probar la carga de documentos individuales"""
    print("=" * 60)
    print("🧪 PROBANDO CARGA DE DOCUMENTOS INDIVIDUALES")
    print("=" * 60)
    print()
    
    sample_dir = "./static/sample_documents"
    all_documents = []
    
    # Test Excel file
    excel_file = os.path.join(sample_dir, "Inventario_Sostenible.xlsx")
    if os.path.exists(excel_file):
        print(f"📊 Cargando Excel: {excel_file}")
        docs = load_excel_with_pandas(excel_file)
        print(f"  ✅ Cargados {len(docs)} documentos")
        if docs:
            print(f"  📄 Contenido: {docs[0].page_content[:200]}...")
            print(f"  🏷️  Metadatos: {docs[0].metadata}")
        all_documents.extend(docs)
        print()
    
    # Test text files
    text_files = [
        "politica_devoluciones.txt",
        "preguntas_frecuentes.txt"
    ]
    
    for filename in text_files:
        file_path = os.path.join(sample_dir, filename)
        if os.path.exists(file_path):
            print(f"📄 Cargando texto: {file_path}")
            docs = load_text_file(file_path)
            print(f"  ✅ Cargados {len(docs)} documentos")
            if docs:
                print(f"  📄 Contenido: {docs[0].page_content[:200]}...")
                print(f"  🏷️  Metadatos: {docs[0].metadata}")
            all_documents.extend(docs)
            print()
    
    print(f"📊 Total de documentos cargados: {len(all_documents)}")
    return all_documents

def test_vector_creation():
    """Probar la creación de la colección vectorial"""
    print("=" * 60)
    print("🧪 PROBANDO CREACIÓN DE COLECCIÓN VECTORIAL")
    print("=" * 60)
    print()
    
    try:
        # Import here to avoid issues with missing API key
        from langchain_chroma import Chroma
        from langchain_openai import OpenAIEmbeddings
        from langchain_text_splitters import CharacterTextSplitter
        from langchain_community.vectorstores.utils import filter_complex_metadata
        import environ
        
        # Set up environment
        env = environ.Env()
        environ.Env.read_env()
        
        # Check if API key is available
        try:
            api_key = env("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY no está configurada")
                return False
        except:
            print("❌ No se puede leer OPENAI_API_KEY")
            return False
        
        print("✅ API key encontrada")
        
        # Load documents
        documents = test_document_loading()
        if not documents:
            print("❌ No hay documentos para procesar")
            return False
        
        print(f"📊 Procesando {len(documents)} documentos...")
        
        # Set up embeddings and text splitter
        embeddings = OpenAIEmbeddings(api_key=api_key)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        
        # Split documents
        texts = text_splitter.split_documents(documents)
        texts = filter_complex_metadata(texts)
        
        print(f"📝 Documentos divididos en {len(texts)} fragmentos")
        
        # Create collection
        persist_directory = "./static/persist"
        os.makedirs(persist_directory, exist_ok=True)
        
        print("🔨 Creando colección vectorial...")
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="sample_documents",
        )
        
        print("✅ Colección creada exitosamente")
        
        # Test retrieval
        print("🔍 Probando recuperación...")
        retriever = vectordb.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.6},
        )
        
        test_query = "¿Cuál es la política de devoluciones?"
        docs = retriever.get_relevant_documents(test_query)
        print(f"📊 Documentos relevantes para '{test_query}': {len(docs)}")
        
        for i, doc in enumerate(docs[:2]):
            print(f"  Documento {i+1}: {doc.page_content[:100]}...")
        
        return len(docs) > 0
        
    except Exception as e:
        print(f"❌ Error en test de vector: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando test de carga vectorial...")
    print()
    
    # Test document loading first
    docs = test_document_loading()
    if not docs:
        print("❌ No se pudieron cargar los documentos")
        return
    
    # Test vector creation
    success = test_vector_creation()
    
    if success:
        print("\n🎉 ¡Test de vector completado exitosamente!")
    else:
        print("\n❌ El test de vector falló")

if __name__ == "__main__":
    main()
