# ============================================================
# app.py — EcoMarket RAG Assistant
# Este script contiene la aplicación completa con Gradio,
# funciones auxiliares (Tools) y Retrieval Augmented Generation (RAG).
# Usa tus documentos locales (FAISS) con LangChain y Gradio.
# ============================================================

# 📦 Importar bibliotecas necesarias
import os
import csv
import gradio as gr
import re # Importar el módulo re para expresiones regulares
from dotenv import load_dotenv

# Importaciones de LangChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, UnstructuredExcelLoader, UnstructuredPDFLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Importaciones de langchain_core para Document
from langchain_core.documents import Document

import warnings

# Suprimir advertencias específicas de unstructured o pdfminer si es necesario
warnings.filterwarnings("ignore", category=UserWarning, module='unstructured')
warnings.filterwarnings("ignore", category=FutureWarning) # Puedes ajustar según la advertencia específica


# ==========================
# 1️⃣ Configurar API Key de OpenAI
# ==========================
# ✅ Configurar API key directamente
# Asegúrate de reemplazar "sk-..." con tu clave API real si no usas variables de entorno
os.environ["OPENAI_API_KEY"] = "sk-0Cl-A-hQJjNHbXq-gw7I7YOf8skFRZUjTb9ZWfw5jtT3BlbkFJwbar8XuCy_2IzPF2qw7mHmlp5bYDzUheDDEiFB4jAA"

# Verificar si la API key está configurada
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ La variable de entorno OPENAI_API_KEY no está configurada. Algunas funcionalidades pueden no estar disponibles.")
else:
     print("✅ OPENAI_API_KEY detectada.") # No mostrar la clave completa por seguridad


# ==========================
# 2️⃣ Variables de entorno
# ==========================
# Cargar variables desde .env si existe (opcional)
load_dotenv() # Esto cargará .env si existe, pero la línea anterior ya setea la clave
DATA_DIR = "content"
VECTORSTORE_PATH = "vectorstore"


# ==========================
# 3️⃣ Funciones auxiliares (Tools)
# ==========================
# Funciones para verificar elegibilidad, calcular reembolso y registrar solicitud
def verificar_elegibilidad_producto(entrada: str) -> str:
    """Verifica la elegibilidad de un producto para devolución.
       Puede recibir formato 'pedido;producto;fecha;motivo' o lenguaje natural.
    """
    print(f"DEBUG: verificar_elegibilidad_producto recibió: {entrada}")
    pedido, producto, fecha, motivo = "desconocido", "producto no identificado", "no especificada", "motivo no especificado"

    if ";" in entrada:
        try:
            partes = [x.strip() for x in entrada.split(";", 3)] # Limitar split a 3 para capturar motivo completo
            if len(partes) == 4:
                pedido, producto, fecha, motivo = partes
            else:
                 return "⚠️ Formato incorrecto. Usa: pedido; producto; fecha; motivo"
        except Exception as e:
            return f"⚠️ Error al parsear entrada con ';': {e}. Usa: pedido; producto; fecha; motivo"
    else:
        # Intenta extraer información de lenguaje natural
        entrada_lower = entrada.lower()
        pedido_match = re.search(r"pedido\s*(\d+)", entrada_lower)
        if pedido_match: pedido = pedido_match.group(1)

        producto_match = re.search(
            r"(?:el|la|los|las)\s+([a-záéíóúñ\s]+?)(?=\s*(?:del|de|porque|por|que|llegó|dañado|defectuoso|no corresponde|$))",
            entrada_lower
        )
        if producto_match: producto = producto_match.group(1).strip()

        motivo_match = re.search(r"(dañado|defectuoso|no corresponde)", entrada_lower)
        if motivo_match: motivo = motivo_match.group(1)


        print(f"DEBUG: Extracción NL - Pedido: {pedido}, Producto: {producto}, Motivo: {motivo}")


    # Lógica de elegibilidad simplificada
    motivos_elegibles = ["defectuoso", "dañado", "no corresponde"]
    if motivo.lower() in motivos_elegibles:
        return f"✅ El producto '{producto}' del pedido {pedido} es elegible para devolución por el motivo: {motivo}."
    else:
        return f"❌ El producto '{producto}' del pedido {pedido} no cumple los criterios de devolución por el motivo: {motivo}."


def calcular_monto_reembolso(entrada: str) -> str:
    """Calcula un monto estimado de reembolso.
       Puede recibir formato 'producto;cantidad;precio' o lenguaje natural.
    """
    print(f"DEBUG: calcular_monto_reembolso recibió: {entrada}")
    producto, cantidad, precio = "producto", 0, 0.0

    if ";" in entrada:
        try:
            partes = [x.strip() for x in entrada.split(";", 2)] # Limitar split a 2
            if len(partes) == 3:
                 producto, cantidad_str, precio_str = partes
                 cantidad = int(cantidad_str)
                 precio = float(precio_str)
            else:
                 return "⚠️ Formato incorrecto. Usa: producto; cantidad; precio"
        except ValueError:
            return "⚠️ Cantidad y precio deben ser números. Usa: producto; cantidad; precio"
        except Exception as e:
             return f"⚠️ Error al parsear entrada con ';': {e}. Usa: producto; cantidad; precio"
    else:
         # Intenta extraer información de lenguaje natural
        match = re.search(
            r"(?:reembolso|devolver|compré|quiero un reembolso por|quiero reembolso de)\s*(?:el|la|los|las)?\s*([a-záéíóúñ\s]+?)\s*(?:por)?\s*\$?(\d+(?:\.\d{1,2})?)",
            entrada.lower()
        )
        if match:
            producto = match.group(1).strip()
            cantidad = 1 # Asumir cantidad 1 si no se especifica
            precio = float(match.group(2))
            print(f"DEBUG: Extracción NL - Producto: {producto}, Cantidad: {cantidad}, Precio: {precio}")
        else:
             return "⚠️ No pude entender los datos para calcular el reembolso. Usa: producto; cantidad; precio o describe claramente el producto y precio."

    return f"💵 Monto estimado de reembolso para {cantidad} x '{producto}': ${cantidad * precio:.2f}"


def registrar_solicitud_devolucion(entrada: str) -> str:
    """Registra una solicitud de devolución en un archivo CSV.
       Puede recibir formato 'pedido;producto;motivo' o lenguaje natural.
    """
    print(f"DEBUG: registrar_solicitud_devolucion recibió: {entrada}")
    pedido, producto, motivo = "desconocido", "producto no identificado", "motivo no especificado"

    if ";" in entrada:
        try:
            partes = [x.strip() for x in entrada.split(";", 2)] # Limitar split a 2
            if len(partes) == 3:
                pedido, producto, motivo = partes
            else:
                return "⚠️ Formato incorrecto. Usa: pedido; producto; motivo"
        except Exception as e:
             return f"⚠️ Error al parsear entrada con ';': {e}. Usa: pedido; producto; motivo"
    else:
        # Intenta extraer información de lenguaje natural
        entrada_lower = entrada.lower()
        pedido_match = re.search(r"pedido\s*(\d+)", entrada_lower)
        if pedido_match: pedido = pedido_match.group(1)

        producto_match = re.search(r"(?:el|la|los|las)\s+([a-záéíóúñ\s]+?)(?=\s*(?:del|de|porque|por|que|$))", entrada_lower)
        if producto_match: producto = producto_match.group(1).strip()

        motivo_match = re.search(r"(dañado|defectuoso|no corresponde)", entrada_lower)
        if motivo_match: motivo = motivo_match.group(1)

        print(f"DEBUG: Extracción NL - Pedido: {pedido}, Producto: {producto}, Motivo: {motivo}")


    # Asegurarse de que la carpeta 'data' existe
    os.makedirs("data", exist_ok=True)
    file_path = "data/solicitudes.csv"

    # Escribir en el archivo CSV
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([pedido, producto, motivo])
        return f"📝 Solicitud registrada para '{producto}' del pedido {pedido} con motivo: {motivo}."
    except Exception as e:
        return f"❌ Error al registrar la solicitud en {file_path}: {e}"


# ==========================
# 4️⃣ Crear carpeta 'content' (si no existe)
# ==========================
# En un script standalone, asegúrate de que los archivos estén en la carpeta 'content'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"📁 Carpeta '{DATA_DIR}' creada. Asegúrate de colocar tus documentos aquí (.txt, .csv, .pdf, .xlsx).")
else:
    print(f"📁 Carpeta '{DATA_DIR}' ya existe.")


# ==========================
# 5️⃣ Crear vectorstore con OpenAI embeddings
# ==========================
def crear_vectorstore():
    """Crea y guarda un vectorstore FAISS a partir de documentos en DATA_DIR."""
    print("⚙️ Creando nuevo vectorstore desde documentos...")
    documentos = []
    archivos_cargados = 0

    # Asegúrate de que la carpeta VECTORSTORE_PATH exista para evitar errores al guardar
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)

    for filename in os.listdir(DATA_DIR):
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.isfile(filepath): # Ignorar directorios
             continue
        try:
            if filename.endswith(".txt"):
                loader = TextLoader(filepath)
            elif filename.endswith(".csv"):
                loader = CSVLoader(filepath)
            elif filename.endswith(".xlsx"):
                loader = UnstructuredExcelLoader(filepath)
            elif filename.endswith(".pdf"):
                 # Asegúrate de que poppler-utils esté instalado en el entorno para PDFs
                 loader = UnstructuredPDFLoader(filepath)
            else:
                print(f"⏭️ Saltando archivo '{filename}': Tipo no soportado.")
                continue # Saltar archivos no soportados

            docs = loader.load()
            documentos.extend(docs)
            archivos_cargados += 1
            print(f"✅ '{filename}' cargado.")

        except Exception as e:
            print(f"⚠️ Error al cargar '{filename}': {e}")

    if not documentos:
        # No lanzar error aquí, permitir que la app corra sin RAG si no hay documentos
        print("❌ No se encontraron documentos válidos o hubo errores al cargarlos. El RAG no estará disponible.")
        # Intentar crear un vectorstore vacío para que la carga posterior no falle completamente
        try:
             embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
             # Crear un documento dummy si no hay documentos reales para inicializar FAISS
             # Esto es una solución alternativa si FAISS.from_documents necesita al menos un documento
             from langchain_core.documents import Document
             # Crear un documento dummy solo si realmente no hay documentos
             if not documentos:
                 documentos_para_faiss = [Document(page_content="No hay documentos cargados para el RAG.", metadata={"source": "dummy"})]
             else:
                 documentos_para_faiss = documentos # Usar documentos reales si se cargó alguno a pesar de errores

             db = FAISS.from_documents(documentos_para_faiss, embeddings)
             db.save_local(VECTORSTORE_PATH)
             print("✅ Vectorstore (inicializado) creado.")
             return db
        except Exception as e_empty:
             print(f"❌ Error fatal al intentar inicializar vectorstore: {e_empty}")
             return None # Retornar None si incluso la inicialización falla


    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = splitter.split_documents(documentos)
    print(f"📄 Total de fragmentos generados: {len(texts)}")

    # Asegúrate de que la API key de OpenAI esté disponible aquí
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
         print("⚠️ OPENAI_API_KEY no está configurada. No se pueden crear embeddings.")
         return None

    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
        db = FAISS.from_documents(texts, embeddings)
        db.save_local(VECTORSTORE_PATH)
        print("✅ Vectorstore creado correctamente en:", VECTORSTORE_PATH)
        return db
    except Exception as e:
        print(f"❌ Error al crear los embeddings o el vectorstore: {e}")
        return None # Retornar None si la creación falla


def cargar_o_crear_vectorstore():
    """Carga un vectorstore existente o crea uno nuevo."""
    index_path = os.path.join(VECTORSTORE_PATH, "index.faiss")
    try:
        if not os.path.exists(index_path):
            print("⚙️ No existe vectorstore previo. Creando uno nuevo...")
            return crear_vectorstore()
        else:
            print("✅ Cargando vectorstore existente desde:", VECTORSTORE_PATH)
            # Asegúrate de que la API key de OpenAI esté disponible aquí
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                 print("⚠️ OPENAI_API_KEY no está configurada. No se pueden cargar embeddings.")
                 # Intentar cargar sin embeddings si es posible o retornar None
                 try:
                     db = FAISS.load_local(VECTORSTORE_PATH, allow_dangerous_deserialization=True)
                     print("💾 Vectorstore cargado SIN embeddings (funcionalidad limitada).")
                     return db
                 except Exception as e_no_emb:
                      print(f"❌ Error al cargar vectorstore sin embeddings: {e_no_emb}")
                      return None

            try:
                embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=api_key)
                db = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
                print("💾 Vectorstore cargado correctamente.")
                return db
            except Exception as e_load:
                 print(f"❌ Error al cargar vectorstore CON embeddings: {e_load}")
                 print("🔁 Intentando regenerarlo desde documentos...")
                 return crear_vectorstore()

    except Exception as e:
        print(f"⚠️ Error general al cargar el vectorstore: {e}")
        print("🔁 Intentando regenerarlo desde documentos...")
        return crear_vectorstore()

# Cargar o crear el vectorstore al inicio
vectorstore = cargar_o_crear_vectorstore()


# ==========================
# 6️⃣ LLM (GPT-4o-mini) + RAG
# ==========================
llm = None
rag_chain = None
retriever = None # Inicializar retriever

api_key = os.getenv("OPENAI_API_KEY")

# Solo inicializar LLM y RAG si la API key y el vectorstore están disponibles y el vectorstore no está vacío
# Verificar si el vectorstore tiene documentos reales (no solo el dummy)
vectorstore_tiene_documentos_reales = False
if vectorstore:
    try:
        # Una forma simple de verificar si tiene documentos reales (puede variar según la implementación)
        # Intentar obtener el retriever y ver si tiene documentos (puede fallar si no hay embeddings/api_key)
        if api_key:
            temp_retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
            test_docs = temp_retriever.get_relevant_documents("test query")
            # Check if the test query returned any meaningful documents (not just the dummy)
            if test_docs and not (len(test_docs) == 1 and "dummy" in test_docs[0].metadata.get("source", "")):
                 vectorstore_tiene_documentos_reales = True
                 print("✅ Vectorstore contiene documentos reales.")
            else:
                 print("⚠️ Vectorstore parece estar vacío o solo contiene documento dummy.")
        else:
             print("⚠️ API KEY no disponible, no se puede verificar el contenido del vectorstore.")
    except Exception as e:
         print(f"⚠️ Error al verificar contenido del vectorstore: {e}")


if api_key and vectorstore and vectorstore_tiene_documentos_reales:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=api_key)

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "Eres un asistente de atención al cliente de EcoMarket.\n"
                "Usa el siguiente contexto para responder de forma clara y amable en español.\n"
                "Responde usando únicamente la información contenida en los documentos proporcionados.\n"
                "Si no encuentras la respuesta en los documentos, responde con: \"No tengo esa información en mis registros.\"\n\n"
                "Contexto:\n{context}\n\n"
                "Pregunta: {question}\n"
                "Respuesta:"
            ),
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            chain_type="stuff",
            return_source_documents=False,
            chain_type_kwargs={"prompt": prompt},
        )
        print("✅ Cadena RAG inicializada.")
    except Exception as e:
        print(f"⚠️ Error al inicializar la cadena RAG: {e}")
        rag_chain = None # Asegurarse de que rag_chain sea None si falla la inicialización
        retriever = None
else:
    if not api_key:
        print("⚠️ OPENAI_API_KEY no configurada. La funcionalidad RAG no estará disponible.")
    if not vectorstore:
         print("⚠️ Vectorstore no disponible. La funcionalidad RAG no estará disponible.")
    elif not vectorstore_tiene_documentos_reales:
         print("⚠️ Vectorstore vacío o con documento dummy. La funcionalidad RAG no estará completamente operativa.")


# ==========================
# 7️⃣ Función de chat (Gradio)
# ==========================
def chat_ecomarket(pregunta, historial=[]):
    """Función principal de chat que usa tools o RAG."""
    # Limpiar espacios en blanco de la pregunta
    pregunta = pregunta.strip()

    if not pregunta:
        return "⚠️ Por favor, escribe una pregunta."

    # Priorizar las funciones auxiliares si la pregunta sugiere su uso (ej: tiene ";", o palabras clave)
    # Una implementación más avanzada podría usar un agente para decidir si usar RAG o una tool
    pregunta_lower = pregunta.lower()
    if ";" in pregunta:
        # Si la pregunta contiene ';', intentar usar una tool
        try:
            if "reembolso" in pregunta_lower:
                 return calcular_monto_reembolso(pregunta)
            elif "registrar" in pregunta_lower or "solicitud" in pregunta_lower:
                 return registrar_solicitud_devolucion(pregunta)
            else: # Por defecto, si tiene ";" pero no las otras palabras clave, usar verificar elegibilidad
                 return verificar_elegibilidad_producto(pregunta)
        except Exception as e:
             print(f"⚠️ Error al procesar solicitud con ';': {e}")
             return f"⚠️ Ocurrió un error al procesar tu solicitud con ';'. Por favor, verifica el formato."
    # Considerar palabras clave para activar tools incluso sin ";" si la intención es clara
    elif "reembolso" in pregunta_lower or "me devuelven" in pregunta_lower or "cuanto me dan" in pregunta_lower:
         # Intentar activar calcular_monto_reembolso si la pregunta parece relacionada
         print("DEBUG: Intentando activar calcular_monto_reembolso por palabras clave.")
         return calcular_monto_reembolso(pregunta) # Pasa la pregunta original para que la función la parsee

    elif "devolver" in pregunta_lower or "devolución" in pregunta_lower or "producto dañado" in pregunta_lower or "producto defectuoso" in pregunta_lower:
         # Intentar activar verificar_elegibilidad_producto si la pregunta parece relacionada
         print("DEBUG: Intentando activar verificar_elegibilidad_producto por palabras clave.")
         return verificar_elegibilidad_producto(pregunta) # Pasa la pregunta original para que la función la parsee

    elif "registrar" in pregunta_lower or "solicitud" in pregunta_lower or "anotar" in pregunta_lower:
         # Intentar activar registrar_solicitud_devolucion si la pregunta parece relacionada
         print("DEBUG: Intentando activar registrar_solicitud_devolucion por palabras clave.")
         return registrar_solicitud_devolucion(pregunta) # Pasa la pregunta original para que la función la parsee


    # Si no contiene ";" y no activa ninguna tool por palabras clave, usar la cadena RAG si está disponible
    if rag_chain:
        try:
            respuesta = rag_chain.invoke({"query": pregunta})
            # Verificar si la respuesta de RAG es válida
            result_text = respuesta.get("result", "").strip()
            if not result_text or "no tengo esa información" in result_text.lower():
                 return "No tengo esa información en mis registros."
            return result_text
        except Exception as e:
            print(f"⚠️ Error en la cadena RAG: {e}")
            return "⚠️ Ocurrió un error al procesar tu pregunta con RAG."
    else:
        # Si rag_chain no está disponible
        return "No tengo esa información en mis registros (Funcionalidad RAG no activa). Asegúrate de tener la API key configurada y documentos cargados en 'content'."


# ==========================
# 8️⃣ UI con Gradio
# ==========================
# Solo lanzar la interfaz si se ejecuta como script principal
if __name__ == "__main__":
    print("\n🚀 Iniciando interfaz de Gradio...")
    demo = gr.ChatInterface(
        fn=chat_ecomarket,
        title="🛍️ Asistente EcoMarket (RAG + Tools + OpenAI)",
        description="Haz preguntas sobre tus productos, pedidos o devoluciones. Usa ';' para comandos específicos (ej: `pedido;producto;motivo`) o describe tu consulta en lenguaje natural.",
        # Puedes añadir ejemplos si lo deseas
        examples=[
            "¿Qué productos ecológicos venden?",
            "¿Cuál es la política de devoluciones?",
            "Quiero devolver el Shampoo Ecológico del pedido 123 porque llegó dañado.", # Ejemplo con lenguaje natural
            "¿Cuánto me devuelven por 2 unidades del Jabón Artesanal que compré a $5.50 cada uno?", # Ejemplo con lenguaje natural
            "Registrar solicitud para pedido 456, producto Crema Facial, motivo no corresponde.", # Ejemplo con lenguaje natural
            "12345; Camiseta de algodón orgánico; 2023-11-01; dañado", # Ejemplo con formato de tool
            "Jabon; 3; 15.75", # Ejemplo con formato de tool
            "pedido_789; Detergente líquido; envase roto", # Ejemplo con formato de tool
        ],
    )
    # Para ejecutar en Colab, share=True es útil
    # Para ejecutar localmente, share=False
    demo.launch(debug=True, share=True)
