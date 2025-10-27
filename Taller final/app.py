import streamlit as st
import os
import csv
from dotenv import load_dotenv

# 🧠 Importar tus funciones personalizadas
from agent_runner import crear_vectorstore, cargar_agente

# ✅ Nuevos imports compatibles
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain import hub

# --- Configuración inicial ---
st.set_page_config(page_title="Ecomarker AI", page_icon="🤖")

st.title("🤖 Asistente Ecomarker Inteligente")
st.write("Haz preguntas sobre productos, pedidos o devoluciones, y el asistente se encargará automáticamente.")

# --- Crear vectorstore si no existe ---
VECTORSTORE_PATH = "vectorstore"
if not os.path.exists(VECTORSTORE_PATH):
    st.info("📄 Creando vectorstore a partir de documentos...")
    crear_vectorstore()
    st.success("✅ Vectorstore creado.")

# --- Inicializar historial en sesión ---
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- Cargar modelo una sola vez ---
if "llm" not in st.session_state:
    with st.spinner("🤖 Cargando modelo FLAN-T5, esto puede tardar un poco la primera vez..."):
        st.session_state.llm = cargar_agente()
    st.success("✅ Modelo cargado correctamente.")

# --- Definir funciones de devolución ---
def verificar_elegibilidad_producto(input: str) -> str:
    try:
        pedido, producto, fecha, motivo = [x.strip() for x in input.split(";")]
    except:
        return "Formato incorrecto. Usa: pedido; producto; fecha; motivo"
    if motivo.lower() in ["defectuoso", "dañado", "no corresponde"]:
        return f"El producto '{producto}' del pedido {pedido} es elegible para devolución."
    else:
        return f"El producto '{producto}' del pedido {pedido} no cumple con los criterios de devolución."

def calcular_monto_reembolso(input: str) -> str:
    try:
        producto, cantidad, precio = [x.strip() for x in input.split(";")]
        cantidad = int(cantidad)
        precio = float(precio)
    except:
        return "Formato incorrecto. Usa: producto; cantidad; precio"
    total = cantidad * precio
    return f"💵 El monto estimado del reembolso por {cantidad} unidades de '{producto}' a ${precio:.2f} cada una es de ${total:.2f}."

def registrar_solicitud_devolucion(input: str) -> str:
    try:
        pedido, producto, motivo = [x.strip() for x in input.split(";")]
    except:
        return "Formato incorrecto. Usa: pedido; producto; motivo"
    ruta = os.path.join("data", "solicitudes.csv")
    os.makedirs("data", exist_ok=True)
    with open(ruta, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([pedido, producto, motivo])
    return f"✅ Solicitud de devolución registrada para el producto '{producto}' del pedido {pedido}."

# --- Definir herramientas del agente ---
tools = [
    Tool(
        name="Elegibilidad Producto",
        func=verificar_elegibilidad_producto,
        description="Verifica si un producto es elegible para devolución. Recibe: pedido; producto; fecha; motivo"
    ),
    Tool(
        name="Calcular Reembolso",
        func=calcular_monto_reembolso,
        description="Calcula el monto estimado de reembolso. Recibe: producto; cantidad; precio"
    ),
    Tool(
        name="Registrar Solicitud",
        func=registrar_solicitud_devolucion,
        description="Registra la solicitud de devolución. Recibe: pedido; producto; motivo"
    ),
]

# --- Crear el agente ---
if "agent" not in st.session_state:
    prompt = hub.pull("hwchase17/react")  # plantilla de razonamiento estándar
    agent = create_react_agent(st.session_state.llm, tools, prompt)
    st.session_state.agent = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

# --- Input del usuario ---
pregunta = st.text_input("Escribe tu pregunta o solicitud:")

if st.button("Enviar") and pregunta:
    with st.spinner("🧠 Procesando tu solicitud..."):
        try:
            respuesta = st.session_state.agent.invoke({"input": pregunta})
            respuesta_texto = respuesta.get("output", "⚠️ No se generó respuesta.")
            st.session_state.historial.append({"pregunta": pregunta, "respuesta": respuesta_texto})
        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

# --- Mostrar historial ---
if st.session_state.historial:
    st.markdown("### 📝 Historial de conversación")
    for turno in st.session_state.historial:
        st.markdown(f"**Tú:** {turno['pregunta']}")
        st.markdown(f"**Asistente:** {turno['respuesta']}")
        st.markdown("---")

st.caption("Nota: La primera vez que uses el modelo FLAN-T5 puede tardar un poco en cargar desde Hugging Face Hub.")












