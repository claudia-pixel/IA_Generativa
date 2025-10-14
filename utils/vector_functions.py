import os
import glob
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
    UnstructuredExcelLoader,
)
import environ

env = environ.Env()
# reading .env file
environ.Env.read_env()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=env("OPENAI_API_KEY"),
)

embeddings = OpenAIEmbeddings(
    api_key=env("OPENAI_API_KEY"),
)

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)


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
    elif file_extension == ".pdf":
        loader = PyPDFLoader(file_path)
    elif file_extension == ".docx":
        loader = Docx2txtLoader(file_path)
    elif file_extension == ".csv":
        loader = CSVLoader(file_path)
    elif file_extension == ".html":
        loader = UnstructuredHTMLLoader(file_path)
    elif file_extension == ".md":
        loader = UnstructuredMarkdownLoader(file_path)
    elif file_extension in [".xlsx", ".xls"]:
        loader = UnstructuredExcelLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    return loader.load()


def create_collection(collection_name, documents):
    """
    Create a new Chroma collection from the given documents.

    Args:
    collection_name (str): The name of the collection to create.
    documents (list): A list of documents to add to the collection.

    Returns:
    None

    This function splits the documents into texts, creates a new Chroma collection,
    and persists it to disk.
    """
    # Split the documents into smaller text chunks
    texts = text_splitter.split_documents(documents)
    persist_directory = "./static/persist"

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
    persist_directory = "./static/persist"
    # Load the Chroma collection from the specified directory
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name,
    )

    return vectordb


def load_retriever(collection_name, score_threshold: float = 0.6):
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
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": score_threshold},
    )
    return retriever


def generate_answer_from_context(retriever, question: str):
    """
    Ask a question and get an answer based on the provided context.

    Args:
        retriever: A retriever object to fetch relevant context.
        question (str): The question to be answered.

    Returns:
        str: The answer to the question based on the retrieved context.
    """
    # Define the message template for the prompt
    message = """
    Answer this question using the provided context only.

    {question}

    Context:
    {context}
    """

    # Create a chat prompt template from the message
    prompt = ChatPromptTemplate.from_messages([("human", message)])

    # Create a RAG (Retrieval-Augmented Generation) chain
    # This chain retrieves context, passes through the question,
    # formats the prompt, and generates an answer using the language model
    rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | llm

    # Invoke the RAG chain with the question and return the generated content
    return rag_chain.invoke(question).content


def add_documents_to_collection(vectordb, documents):
    """
    Add documents to the vector database collection.

    Args:
        vectordb: The vector database object to add documents to.
        documents: A list of documents to be added to the collection.

    This function splits the documents into smaller chunks, adds them to the
    vector database, and persists the changes.
    """

    # Split the documents into smaller text chunks
    texts = text_splitter.split_documents(documents)

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
    sample_dir = "./static/sample_documents"
    collection_name = "sample_documents"
    
    if not os.path.exists(sample_dir):
        print(f"❌ Directory {sample_dir} not found")
        return [], collection_name
    
    # Get all supported file types
    supported_extensions = [".txt", ".pdf", ".docx", ".csv", ".html", ".md", ".xlsx", ".xls"]
    all_documents = []
    
    print(f"📁 Loading sample documents from {sample_dir}...")
    
    for ext in supported_extensions:
        pattern = os.path.join(sample_dir, f"*{ext}")
        files = glob.glob(pattern)
        
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
                import traceback
                traceback.print_exc()
    
    print(f"📊 Total sample documents loaded: {len(all_documents)}")
    return all_documents, collection_name


def initialize_sample_collection():
    """
    Initialize the sample documents collection.
    This function loads all sample documents and creates/updates the collection.
    
    Returns:
    bool: True if successful, False otherwise.
    """
    try:
        print("🔄 Starting sample collection initialization...")
        
        # Load sample documents
        documents, collection_name = load_sample_documents()
        
        if not documents:
            print("⚠️  No sample documents found to load")
            return False
        
        print(f"📊 Loaded {len(documents)} documents from sample files")
        
        # Always create/update the collection
        persist_directory = "./static/persist"
        os.makedirs(persist_directory, exist_ok=True)
        
        # Check if collection already exists
        collection_path = os.path.join(persist_directory, "chroma.sqlite3")
        
        if os.path.exists(collection_path):
            try:
                # Try to load existing collection
                existing_collection = load_collection(collection_name)
                print(f"📚 Found existing collection: {collection_name}")
                
                # Add new documents to existing collection
                add_documents_to_collection(existing_collection, documents)
                print(f"✅ Added {len(documents)} documents to existing collection")
                
            except Exception as e:
                print(f"📝 Error loading existing collection, creating new one: {e}")
                # Create new collection
                vectordb = create_collection(collection_name, documents)
                if not vectordb:
                    print("❌ Failed to create sample documents collection")
                    return False
                print(f"✅ Sample documents collection created successfully with {len(documents)} documents")
        else:
            # Create new collection
            print(f"📝 Creating new collection: {collection_name}")
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
        import traceback
        traceback.print_exc()
        return False


def register_sample_documents_in_db():
    """
    Register sample documents in the database so they appear in admin panel.
    """
    try:
        from models.db import create_source
        
        sample_dir = "./static/sample_documents"
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
                from models.db import connect_db
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


def get_combined_retriever(score_threshold: float = 0.6):
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