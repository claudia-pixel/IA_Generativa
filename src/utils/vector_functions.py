import os
import glob
import time
import traceback
import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.vectorstores.utils import filter_complex_metadata
import environ

# Importar traceable si está disponible
try:
    from langsmith import traceable
    TRACEABLE_DECORATOR = traceable
except ImportError:
    # Si no está disponible, usar decorador vacío
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    TRACEABLE_DECORATOR = traceable

# Importar módulos locales
from utils.tracing import tracer, log_retrieval, log_generation
try:
    from templates.agent_prompts import get_rag_prompt_template
except ImportError:
    get_rag_prompt_template = None

env = environ.Env()
# reading .env file
environ.Env.read_env()

def get_base_dir():
    """Obtener el directorio base del proyecto (dos niveles arriba desde src/utils/)"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar LangSmith tracing ANTES de inicializar los modelos
def _configure_langsmith_tracing():
    """Configurar LangSmith tracing si está habilitado"""
    langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false")
    langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
    
    tracing_enabled = (
        langsmith_tracing.lower() == "true" or
        langchain_tracing_v2.lower() == "true"
    )
    
    if tracing_enabled:
        api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
        api_url = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        project_name = os.getenv("LANGCHAIN_PROJECT", "ecomarket-rag-system")
        
        if api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = api_url
            os.environ["LANGCHAIN_API_KEY"] = api_key
            os.environ["LANGCHAIN_PROJECT"] = project_name
            print(f"✅ LangSmith tracing configurado - Proyecto: {project_name}")
        else:
            print("⚠️  LangSmith tracing habilitado pero no se encontró API_KEY")
    else:
        print("ℹ️  LangSmith tracing deshabilitado")

# Configurar tracing antes de inicializar modelos
_configure_langsmith_tracing()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=env("OPENAI_API_KEY"),
)

embeddings = OpenAIEmbeddings(
    api_key=env("OPENAI_API_KEY"),
)

def create_optimal_splitter(file_type: str, content: str = ""):
    """
    Crear splitter optimizado basado en el tipo de contenido.
    
    Args:
        file_type (str): Tipo de archivo (excel, txt, pdf, etc.)
        content (str): Contenido del documento para análisis
    
    Returns:
        CharacterTextSplitter: Splitter optimizado para el tipo de contenido
    """
    # Detectar si es contenido estructurado (Excel, CSV, etc.)
    is_structured = (
        file_type in ["excel", "csv"] or 
        "Fila" in content or 
        "Columnas" in content or
        "Nombre del Producto" in content
    )
    
    if is_structured:
        # Para datos estructurados: fragmentos medianos
        return CharacterTextSplitter(
            chunk_size=500,     # Fragmentos más grandes para capturar más productos
            chunk_overlap=50,   # Buena superposición para contexto
            length_function=len,
            separator="\n"
        )
    else:
        # Para texto narrativo: fragmentos más grandes
        return CharacterTextSplitter(
            chunk_size=500,     # Más grande para texto narrativo
            chunk_overlap=50,   # Más superposición
            length_function=len,
            separator="\n"
        )

# Splitter por defecto (para compatibilidad)
text_splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separator="\n"
)


def load_excel_with_pandas(file_path: str) -> list[Document]:
    """
    Load Excel file using pandas and create one Document per product row.
    Each product becomes a separate chunk with rich metadata.
    
    Args:
        file_path (str): Path to the Excel file.
    
    Returns:
        list[Document]: A list of Document objects, one per product row.
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        
        documents = []
        
        if df.empty:
            return documents
        
        # Normalize column names to handle variations
        def normalize_column_name(col_name: str) -> str:
            """Normalize column names to standard format"""
            col_lower = col_name.lower().strip()
            
            # Map common variations to standard names
            if 'nombre' in col_lower and ('producto' in col_lower or 'product' in col_lower):
                return 'producto_nombre'
            elif 'producto' in col_lower:
                return 'producto_nombre'
            elif 'categoria' in col_lower or 'category' in col_lower:
                return 'categoria'
            elif 'cantidad' in col_lower or ('stock' in col_lower or 'quantity' in col_lower):
                return 'cantidad'
            elif 'precio' in col_lower or 'price' in col_lower:
                if 'unitario' in col_lower or 'unit' in col_lower:
                    return 'precio'
                else:
                    return 'precio'
            elif 'fecha' in col_lower or 'date' in col_lower:
                return 'fecha'
            else:
                return col_name
        
        # Create a mapping of normalized names to original names
        column_mapping = {normalize_column_name(col): col for col in df.columns}
        
        # Create one Document per row (product)
        for index, row in df.iterrows():
            # Extract metadata
            producto_nombre = None
            categoria = None
            cantidad = None
            precio = None
            fecha = None
            
            # Try to extract data from the row using normalized column names
            for normalized_col, original_col in column_mapping.items():
                value = row[original_col]
                if pd.notna(value):
                    if normalized_col == 'producto_nombre':
                        producto_nombre = str(value)
                    elif normalized_col == 'categoria':
                        categoria = str(value)
                    elif normalized_col == 'cantidad':
                        cantidad = str(value) if not isinstance(value, (int, float)) else str(int(value))
                    elif normalized_col == 'precio':
                        precio = str(value)
                    elif normalized_col == 'fecha':
                        fecha = str(value)
            
            # Create a readable text content for the chunk
            chunk_content_parts = []
            
            if producto_nombre:
                chunk_content_parts.append(f"Producto: {producto_nombre}")
            if categoria:
                chunk_content_parts.append(f"Categoría: {categoria}")
            if cantidad:
                chunk_content_parts.append(f"Cantidad en Stock: {cantidad}")
            if precio:
                chunk_content_parts.append(f"Precio: {precio}")
            if fecha:
                chunk_content_parts.append(f"Fecha: {fecha}")
            
            # Also include all columns to ensure we don't lose information
            for col in df.columns:
                value = row[col]
                if pd.notna(value):
                    chunk_content_parts.append(f"{col}: {value}")
            
            chunk_content = " | ".join(chunk_content_parts)
            
            # Create metadata dictionary
            metadata = {
                "source": file_path,
                "file_type": "excel",
                "source_type": "inventory",
                "row_index": index,
                "total_rows": len(df)
            }
            
            # Add product-specific metadata
            if producto_nombre:
                metadata["producto_nombre"] = producto_nombre
            if categoria:
                metadata["categoria"] = categoria
            if cantidad:
                metadata["cantidad"] = cantidad
            if precio:
                metadata["precio"] = precio
            if fecha:
                metadata["fecha"] = fecha
            
            # Create document for this product
            document = Document(
                page_content=chunk_content,
                metadata=metadata
            )
            
            documents.append(document)
        
        print(f"✅ Loaded {len(documents)} products from Excel file")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error loading Excel file with pandas: {e}")
        import traceback
        traceback.print_exc()
        return []


def load_document(file_path: str) -> list[Document]:
    """
    Load a document from a file path.
    Supports .txt, .pdf, .docx, .csv, .html, .md, and .xlsx files.

    Args:
    file_path (str): Path to the document file.

    Returns:
    list[Document]: A list of Document objects.

    Raises:
    ValueError: If the file type is not supported.
    """
    _, file_extension = os.path.splitext(file_path)

    if file_extension == ".txt":
        loader = TextLoader(file_path)
        return loader.load()
    elif file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif file_extension == ".docx":
        loader = Docx2txtLoader(file_path)
        return loader.load()
    elif file_extension == ".csv":
        loader = CSVLoader(file_path)
        return loader.load()
    elif file_extension == ".html":
        loader = UnstructuredHTMLLoader(file_path)
        return loader.load()
    elif file_extension == ".md":
        loader = UnstructuredMarkdownLoader(file_path)
        return loader.load()
    elif file_extension in [".xlsx", ".xls"]:
        # Use pandas for Excel files (more reliable)
        return load_excel_with_pandas(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def create_collection(collection_name, documents):
    """
    Create a new Chroma collection from the given documents using adaptive chunking.

    Args:
    collection_name (str): The name of the collection to create.
    documents (list): A list of documents to add to the collection.

    Returns:
    None

    This function splits the documents into texts using adaptive chunking strategy,
    creates a new Chroma collection, and persists it to disk.
    """
    # Use adaptive chunking strategy
    all_texts = []
    
    for doc in documents:
        # Determine file type from metadata or content
        file_type = doc.metadata.get('file_type', 'unknown')
        content = doc.page_content
        
        # For Excel files, check if it's already chunked at product level
        # (has row_index metadata indicating it's a single product chunk)
        if file_type == 'excel' and 'row_index' in doc.metadata:
            # This is already a product-level chunk, don't split further
            all_texts.append(doc)
            print(f"📦 Product chunk (already chunked at product level)")
        else:
            # Create optimal splitter for this document
            optimal_splitter = create_optimal_splitter(file_type, content)
            
            # Split this specific document
            doc_texts = optimal_splitter.split_documents([doc])
            all_texts.extend(doc_texts)
            
            print(f"📄 Split {doc.metadata.get('source', 'unknown')} into {len(doc_texts)} chunks (type: {file_type})")
    
    # Filter complex metadata
    texts = filter_complex_metadata(all_texts)
    
    base_dir = get_base_dir()
    persist_directory = os.path.join(base_dir, "static/persist")

    # Create a new Chroma collection from the text chunks
    try:
        vectordb = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name=collection_name,
        )
    except Exception as e:
        print(f"Error creating collection: {e}")
        return None

    return vectordb


def load_collection(collection_name):
    """
    Load an existing Chroma collection.

    Args:
    collection_name (str): The name of the collection to load.

    Returns:
    Chroma: The loaded Chroma collection.

    This function loads a previously created Chroma collection from disk.
    """
    base_dir = get_base_dir()
    persist_directory = os.path.join(base_dir, "static/persist")
    # Load the Chroma collection from the specified directory
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    return vectordb


def load_retriever(collection_name, score_threshold: float = 0.3):
    """
    Create a retriever from a Chroma collection with a similarity score threshold.

    Args:
    collection_name (str): The name of the collection to use.
    score_threshold (float): The minimum similarity score threshold for retrieving documents.
                           Documents with scores below this threshold will be filtered out.
                           Defaults to 0.6.

    Returns:
    Retriever: A retriever object that can be used to query the collection with similarity
              score filtering.

    This function loads a Chroma collection and creates a retriever from it that will only
    return documents meeting the specified similarity score threshold.
    """
    # Load the Chroma collection
    vectordb = load_collection(collection_name)
    # Create a retriever from the collection with specified search parameters
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10},  # Más documentos para preguntas amplias
    )
    return retriever


@TRACEABLE_DECORATOR
def generate_answer_from_context(retriever, question: str, enable_logging: bool = False):
    """
    Ask a question and get an answer based on the provided context.

    Args:
        retriever: A retriever object to fetch relevant context.
        question (str): The question to be answered.
        enable_logging (bool): Whether to enable detailed logging.

    Returns:
        str: The answer to the question based on the retrieved context.
    """
    start_time = time.time()
    
    # Importar y usar el template del sistema
    if get_rag_prompt_template:
        message = get_rag_prompt_template()
    else:
        # Fallback si no se puede importar
        message = """
    Eres un asistente útil. Responde usando ÚNICAMENTE la información del contexto.
    
    Pregunta: {question}
    Contexto: {context}
    Respuesta:
    """

    # Create a chat prompt template from the message
    prompt = ChatPromptTemplate.from_messages([("human", message)])

    # Log retrieved documents if logging is enabled
    retrieved_docs = []
    if enable_logging:
        print(f"🔍 RAG LOGGING - Pregunta: {question}")
        try:
            retrieved_docs = retriever.get_relevant_documents(question)
            print(f"📊 Documentos recuperados: {len(retrieved_docs)}")
            for i, doc in enumerate(retrieved_docs):
                print(f"  📄 Doc {i+1}: {doc.metadata.get('source', 'Unknown')} - {doc.page_content[:100]}...")
        except Exception as e:
            print(f"❌ Error recuperando documentos: {e}")
    
    # Log retrieval para trazabilidad
    if retrieved_docs:
        log_retrieval(question, retrieved_docs)

    # Create a RAG (Retrieval-Augmented Generation) chain
    # This chain retrieves context, passes through the question,
    # formats the prompt, and generates an answer using the language model
    rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

    # Invoke the RAG chain with the question and return the generated content
    response = rag_chain.invoke(question).content
    
    # Log response if logging is enabled
    if enable_logging:
        print(f"🤖 Respuesta generada: {response}")
    
    # Log generation para trazabilidad
    processing_time = time.time() - start_time
    log_generation(question, response, processing_time)
    
    return response


def add_documents_to_collection(vectordb, documents):
    """
    Add documents to the vector database collection.

    Args:
        vectordb: The vector database object to add documents to.
        documents: A list of documents to be added to the collection.

    This function splits the documents into smaller chunks, adds them to the
    vector database, and persists the changes.
    """
    all_texts = []
    
    for doc in documents:
        # Determine file type from metadata
        file_type = doc.metadata.get('file_type', 'unknown')
        
        # For Excel files, check if it's already chunked at product level
        # (has row_index metadata indicating it's a single product chunk)
        if file_type == 'excel' and 'row_index' in doc.metadata:
            # This is already a product-level chunk, don't split further
            all_texts.append(doc)
            print(f"📦 Adding product chunk (already chunked at product level)")
        else:
            # Split the document into smaller text chunks
            doc_texts = text_splitter.split_documents([doc])
            all_texts.extend(doc_texts)
            print(f"📄 Split document into {len(doc_texts)} chunks")
    
    # Filter complex metadata
    texts = filter_complex_metadata(all_texts)

    # Add the text chunks to the vector database
    vectordb.add_documents(texts)

    return vectordb


def load_sample_documents():
    """
    Load all documents from the sample_documents directory.
    
    Returns:
    tuple: (documents, collection_name) - A tuple containing the loaded documents 
           and the collection name for sample documents.
    """
    base_dir = get_base_dir()
    sample_dir = os.path.join(base_dir, "static/sample_documents")
    collection_name = "sample_documents"
    
    if not os.path.exists(sample_dir):
        print(f"❌ Directory {sample_dir} not found")
        return [], collection_name
    
    # Get all supported file types
    supported_extensions = [".txt", ".pdf", ".docx", ".csv", ".html", ".md", ".xlsx", ".xls"]
    all_documents = []
    
    print(f"📁 Loading sample documents from {sample_dir}...")
    
    # List all files in the directory for debugging
    all_files = os.listdir(sample_dir)
    print(f"📋 Files found in directory: {all_files}")
    
    for ext in supported_extensions:
        pattern = os.path.join(sample_dir, f"*{ext}")
        files = glob.glob(pattern)
        print(f"🔍 Looking for {ext} files: found {len(files)} files")
        
        for file_path in files:
            try:
                print(f"  📄 Loading: {os.path.basename(file_path)}")
                documents = load_document(file_path)
                
                # For Excel files, add metadata to help with retrieval
                if ext in [".xlsx", ".xls"]:
                    for doc in documents:
                        doc.metadata["source_type"] = "inventory"
                        doc.metadata["file_type"] = "excel"
                
                all_documents.extend(documents)
                print(f"    ✅ Loaded {len(documents)} document(s)")
                
                # Debug: Print first few characters of each document
                for i, doc in enumerate(documents[:2]):  # Only first 2 docs
                    content_preview = doc.page_content[:100].replace('\n', ' ')
                    print(f"      Preview {i+1}: {content_preview}...")
                    
            except Exception as e:
                print(f"    ❌ Error loading {os.path.basename(file_path)}: {str(e)}")
                traceback.print_exc()
    
    print(f"📊 Total sample documents loaded: {len(all_documents)}")
    return all_documents, collection_name


def is_sample_collection_initialized():
    """
    Check if the sample collection is already initialized.
    
    Returns:
    bool: True if collection exists and has documents, False otherwise.
    """
    try:
        base_dir = get_base_dir()
        persist_directory = os.path.join(base_dir, "static/persist")
        collection_path = os.path.join(persist_directory, "chroma.sqlite3")
        
        if not os.path.exists(collection_path):
            return False
        
        # Try to load the collection
        vectordb = load_collection("sample_documents")
        
        # Check if collection has documents
        collection_count = vectordb._collection.count()
        return collection_count > 0
        
    except Exception:
        return False


def initialize_sample_collection():
    """
    Initialize the sample documents collection.
    This function loads all sample documents and creates/updates the collection.
    
    Returns:
    bool: True if successful, False otherwise.
    """
    try:
        # Check if already initialized
        if is_sample_collection_initialized():
            print("✅ Sample collection already initialized")
            return True
        
        print("🔄 Starting sample collection initialization...")
        
        # Check if sample documents directory exists
        base_dir = get_base_dir()
        sample_dir = os.path.join(base_dir, "static/sample_documents")
        if not os.path.exists(sample_dir):
            print(f"❌ Sample documents directory not found: {sample_dir}")
            return False
        
        # Load sample documents
        documents, collection_name = load_sample_documents()
        
        if not documents:
            print("⚠️  No sample documents found to load")
            return False
        
        print(f"📊 Loaded {len(documents)} documents from sample files")
        
        # Create/update the collection
        base_dir = get_base_dir()
        persist_directory = os.path.join(base_dir, "static/persist")
        os.makedirs(persist_directory, exist_ok=True)
        
        # Create new collection
        print(f"📝 Creating collection: {collection_name}")
        vectordb = create_collection(collection_name, documents)
        if not vectordb:
            print("❌ Failed to create sample documents collection")
            return False
        print(f"✅ Sample documents collection created successfully with {len(documents)} documents")
        
        # Register documents in database
        register_sample_documents_in_db()
        
        # Test the collection
        try:
            test_retriever = load_retriever(collection_name)
            print("✅ Collection test successful - retriever created")
        except Exception as e:
            print(f"⚠️  Collection test failed: {e}")
        
        return True
                
    except Exception as e:
        print(f"❌ Error initializing sample collection: {str(e)}")
        traceback.print_exc()
        return False


def register_sample_documents_in_db():
    """
    Register sample documents in the database so they appear in admin panel.
    """
    # Import condicional de models.db para evitar dependencia circular
    try:
        from models.db import create_source, connect_db
    except ImportError:
        # Si no se puede importar, retornar sin hacer nada
        print("⚠️  No se pudo importar models.db")
        return
    
    try:
        base_dir = get_base_dir()
        sample_dir = os.path.join(base_dir, "static/sample_documents")
        if not os.path.exists(sample_dir):
            return
        
        # Get all sample files
        supported_extensions = [".txt", ".pdf", ".docx", ".csv", ".html", ".md", ".xlsx", ".xls"]
        
        for ext in supported_extensions:
            pattern = os.path.join(sample_dir, f"*{ext}")
            files = glob.glob(pattern)
            
            for file_path in files:
                filename = os.path.basename(file_path)
                
                # Check if document is already registered
                conn = connect_db()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM sources WHERE name = ? AND chat_id = 1 AND type = 'sample_document'",
                    (filename,)
                )
                
                if not cursor.fetchone():
                    # Create description based on filename
                    if "politica" in filename.lower():
                        description = "Política de devoluciones y cambios de EcoMarket"
                    elif "preguntas" in filename.lower():
                        description = "Preguntas frecuentes de EcoMarket"
                    elif "inventario" in filename.lower():
                        description = "Inventario de productos sostenibles"
                    else:
                        description = f"Documento de muestra: {filename}"
                    
                    # Register in database
                    create_source(
                        filename,
                        description,
                        1,  # System chat
                        source_type="sample_document"
                    )
                    print(f"  📝 Registered in DB: {filename}")
                
                conn.close()
        
        print("✅ Sample documents registered in database")
        
    except Exception as e:
        print(f"❌ Error registering sample documents in DB: {str(e)}")


def get_combined_retriever(score_threshold: float = 0.3):
    """
    Get a retriever that combines both sample_documents and ecomarket_kb collections.
    
    Args:
        score_threshold (float): The minimum similarity score threshold for retrieving documents.
    
    Returns:
        Retriever: A combined retriever that searches both collections.
    """
    try:
        # Try to load sample documents collection first
        sample_retriever = None
        try:
            sample_retriever = load_retriever("sample_documents", score_threshold)
            print("✅ Sample documents retriever loaded")
        except Exception as e:
            print(f"⚠️  Could not load sample documents: {e}")
        
        # Try to load regular documents collection
        regular_retriever = None
        try:
            regular_retriever = load_retriever("ecomarket_kb", score_threshold)
            print("✅ Regular documents retriever loaded")
        except Exception as e:
            print(f"⚠️  Could not load regular documents: {e}")
        
        # Return the available retriever
        if sample_retriever:
            return sample_retriever
        elif regular_retriever:
            return regular_retriever
        else:
            raise Exception("No collections available")
            
    except Exception as e:
        print(f"❌ Error getting combined retriever: {e}")
        raise e


def test_sample_documents():
    """
    Test function to verify that sample documents are loaded correctly.
    """
    try:
        print("🧪 Testing sample documents loading...")
        
        # Test loading sample documents
        documents, collection_name = load_sample_documents()
        print(f"📊 Loaded {len(documents)} documents from {collection_name}")
        
        if documents:
            # Test creating/loading collection
            try:
                vectordb = load_collection(collection_name)
                print(f"✅ Collection '{collection_name}' loaded successfully")
                
                # Test retriever
                retriever = load_retriever(collection_name)
                print("✅ Retriever created successfully")
                
                # Test a sample query
                test_query = "¿Cuál es la política de devoluciones?"
                print(f"🔍 Testing query: {test_query}")
                
                try:
                    response = generate_answer_from_context(retriever, test_query)
                    print(f"✅ Query response: {response[:100]}...")
                    return True
                except Exception as e:
                    print(f"❌ Error testing query: {e}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error loading collection: {e}")
                return False
        else:
            print("❌ No documents loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False