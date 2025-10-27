"""
Agente de Respuesta - Genera respuestas amigables e interactúa con usuarios
Responsabilidad: Generar respuestas conversacionales y amigables
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tracing import tracer
from templates.agent_reasoning import get_agent_final_response_prompt, get_reasoning_prompt

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    from langsmith import traceable
    TRACEABLE_AVAILABLE = True
except ImportError:
    TRACEABLE_AVAILABLE = False
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class ResponseAgent:
    """
    Agente de Respuesta que genera respuestas amigables y conversacionales.
    Su función es tomar los resultados de las herramientas y generar una respuesta natural.
    """
    
    def __init__(self):
        """Inicializar el agente de respuesta"""
        self.llm_response = None
        self._initialize()
    
    def _initialize(self):
        """Inicializar el LLM para respuestas"""
        if not LLM_AVAILABLE:
            print("⚠️  LLM no disponible para respuestas")
            return
        
        try:
            from utils.vector_functions import env
            
            # LLM para respuestas - temperatura media para ser conversacional
            self.llm_response = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=env("OPENAI_API_KEY"),
                temperature=0.7  # Temperatura media-alta para respuestas más naturales y amigables
            )
            print("✅ Response Agent inicializado")
        except Exception as e:
            print(f"⚠️  Error inicializando LLM para respuestas: {e}")
            self.llm_response = None
    
    @traceable(name="ResponseAgent.generate_response")
    def generate_response(self, analysis: dict, tool_results: dict, original_query: str, trace_id: str = None) -> str:
        """
        Generar respuesta final usando LLM.
        
        Args:
            analysis: Análisis del orquestador
            tool_results: Resultados de las herramientas
            original_query: Consulta original del usuario
            trace_id: ID del trace para agrupar logs
            
        Returns:
            str: Respuesta amigable y conversacional
        """
        if not self.llm_response:
            return self._format_simple_response(tool_results)
        
        try:
            # Preparar datos para el prompt
            retrieved_data = self._format_tool_results(tool_results)
            
            # Obtener prompt de respuesta final
            response_prompt_template = get_agent_final_response_prompt()
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_reasoning_prompt("system_context")),
                ("human", response_prompt_template)
            ])
            
            # Log inicio de generación de respuesta
            tracer.log(
                operation="RESPONSE_GENERATION_START",
                message="Iniciando generación de respuesta amigable",
                metadata={
                    "original_query": original_query[:100],
                    "tools_used": tool_results.get("tools_used", [])
                },
                level="INFO",
                trace_id=trace_id
            )
            
            # Generar respuesta usando LLM de respuestas (conversacional)
            chain = prompt | self.llm_response
            response = chain.invoke({
                "retrieved_data": retrieved_data,
                "original_query": original_query,
                "tools_used": ", ".join(tool_results.get("tools_used", []))
            }).content
            
            # Log respuesta generada exitosamente
            tracer.log(
                operation="RESPONSE_GENERATED",
                message="Respuesta generada exitosamente por Response Agent",
                metadata={
                    "response_length": len(response),
                    "tools_used": tool_results.get("tools_used", []),
                    "intent": analysis.get("intent", "N/A")
                },
                level="SUCCESS",
                trace_id=trace_id
            )
            
            return response
            
        except Exception as e:
            tracer.log(
                operation="RESPONSE_GENERATION_ERROR",
                message=f"Error generando respuesta: {str(e)}",
                level="ERROR",
                trace_id=trace_id
            )
            return self._format_simple_response(tool_results)
    
    def _format_tool_results(self, results: dict) -> str:
        """Formatear resultados de herramientas para el prompt"""
        formatted = "📊 INFORMACIÓN RECUPERADA:\n\n"
        
        for tool, data in results.get("data", {}).items():
            formatted += f"**{tool}:**\n"
            
            if isinstance(data, dict):
                if "result" in data:
                    result = data["result"]
                    if isinstance(result, str):
                        formatted += result
                    else:
                        formatted += str(result)
                elif "mensaje" in data:
                    formatted += data["mensaje"]
                else:
                    formatted += str(data)
            else:
                formatted += str(data)
            
            formatted += "\n\n"
        
        return formatted
    
    def _format_simple_response(self, results: dict) -> str:
        """Generar respuesta simple sin LLM (fallback)"""
        response = ""
        
        for tool, data in results.get("data", {}).items():
            if isinstance(data, dict):
                if "result" in data:
                    result = data["result"]
                    if isinstance(result, str):
                        response += result + "\n\n"
                elif "mensaje" in data:
                    response += data["mensaje"] + "\n\n"
            elif isinstance(data, str):
                response += data + "\n\n"
        
        if not response:
            response = "Hola! 🌿 Lo siento, no pude procesar tu solicitud en este momento. Por favor, intenta de nuevo o contáctanos directamente."
        
        return response
    
    def request_missing_info(self, missing_info: list, intent: str) -> str:
        """
        Solicitar información faltante al usuario de manera amigable.
        
        Args:
            missing_info: Lista de información faltante
            intent: Intención del usuario
            
        Returns:
            str: Mensaje solicitando información
        """
        response = f"""
¡Hola! 👋 Para ayudarte con '{intent}', necesito un poco más de información:

"""
        
        for info in missing_info:
            response += f"📋 {info}\n"
        
        response += "\nPor favor, proporciona esta información y estaré encantada de ayudarte. 🌿"
        
        return response


# Singleton global
_response_instance = None

def get_response_agent():
    """Obtener instancia global del agente de respuesta"""
    global _response_instance
    if _response_instance is None:
        _response_instance = ResponseAgent()
    return _response_instance

