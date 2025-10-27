"""
Agente Orquestador - Analiza consultas y decide qué hacer
Responsabilidad: Reasoning y toma de decisiones
"""

import os
import sys
import json
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tracing import tracer
from templates.agent_reasoning import get_agent_reasoning_prompt, get_reasoning_prompt
from agents.rag_agent import EcoMarketAgent
from tools.chat_memory import store_chat_memory, retrieve_chat_memory, extract_user_info, get_context_for_query

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


class OrchestratorAgent:
    """
    Agente Orquestador que analiza consultas y decide qué herramientas usar.
    Su función es hacer reasoning y orquestar las herramientas.
    """
    
    def __init__(self):
        """Inicializar el agente orquestador"""
        self.llm_reasoning = None
        self.rag_agent = EcoMarketAgent()
        self._initialize()
    
    def _initialize(self):
        """Inicializar el LLM para reasoning"""
        if not LLM_AVAILABLE:
            print("⚠️  LLM no disponible para reasoning")
            return
        
        try:
            from utils.vector_functions import env
            
            # LLM específico para reasoning - temperatura muy baja para precisión
            self.llm_reasoning = ChatOpenAI(
                model="gpt-4o-mini",
                api_key=env("OPENAI_API_KEY"),
                temperature=0.1  # Muy baja temperatura para reasoning preciso
            )
            print("✅ Orchestrator Agent inicializado")
        except Exception as e:
            print(f"⚠️  Error inicializando LLM para reasoning: {e}")
            self.llm_reasoning = None
    
    def is_ready(self):
        """Verificar si el agente está listo"""
        return self.rag_agent.is_ready()
    
    @traceable(name="OrchestratorAgent.analyze_query")
    def analyze_query(self, query: str, trace_id: str = None) -> dict:
        """
        Analizar la consulta del usuario usando reasoning.
        
        Args:
            query: Consulta del usuario
            trace_id: ID del trace para agrupar logs
            
        Returns:
            dict: Análisis con herramientas a usar y datos extraídos
        """
        if not self.llm_reasoning:
            # Si no hay LLM, usar heurística simple
            return self._simple_analysis(query)
        
        try:
            # Obtener prompt de reasoning
            reasoning_prompt_template = get_agent_reasoning_prompt()
            prompt = ChatPromptTemplate.from_messages([
                ("system", get_reasoning_prompt("system_context")),
                ("human", reasoning_prompt_template)
            ])
            
            # Log inicio de reasoning
            tracer.log(
                operation="LLM_REASONING_START",
                message="Iniciando reasoning con LLM",
                metadata={"query": query[:100]},
                level="INFO",
                trace_id=trace_id
            )
            
            # Generar análisis usando LLM de reasoning
            chain = prompt | self.llm_reasoning
            response = chain.invoke({"user_query": query}).content
            
            # Log reasoning completado
            tracer.log(
                operation="LLM_REASONING_COMPLETE",
                message="Reasoning completado",
                metadata={"response_length": len(response)},
                level="SUCCESS",
                trace_id=trace_id
            )
            
            # Parsear JSON
            try:
                analysis = json.loads(response)
                tracer.log(
                    operation="REASONING_ANALYSIS",
                    message="Análisis de consulta completado por Orchestrator",
                    metadata=analysis,
                    level="INFO",
                    trace_id=trace_id
                )
                return analysis
            except json.JSONDecodeError:
                print("⚠️  No se pudo parsear JSON, usando heurística")
                return self._simple_analysis(query)
                
        except Exception as e:
            tracer.log(
                operation="REASONING_ERROR",
                message=f"Error en reasoning: {str(e)}",
                level="ERROR",
                trace_id=trace_id
            )
            return self._simple_analysis(query)
    
    def _simple_analysis(self, query: str) -> dict:
        """Análisis heurístico simple cuando no hay LLM"""
        query_lower = query.lower()
        
        # Detección heurística
        if "ticket" in query_lower:
            if "consultar" in query_lower or "ver" in query_lower or "TKT-" in query:
                return {
                    "intent": "Consultar ticket existente",
                    "tools_needed": ["TICKET_QUERY"],
                    "reasoning": "Menciona consultar ticket",
                    "requires_additional_info": False
                }
            else:
                return {
                    "intent": "Crear ticket",
                    "tools_needed": ["TICKET_CREATE"],
                    "reasoning": "Menciona ticket sin consulta",
                    "requires_additional_info": True,
                    "missing_info": ["tipo de ticket"]
                }
        
        elif "producto" in query_lower or "inventario" in query_lower:
            return {
                "intent": "Buscar productos",
                "tools_needed": ["PRODUCT_SEARCH"],
                "reasoning": "Pregunta sobre productos",
                "requires_additional_info": False
            }
        
        else:
            return {
                "intent": "Consultar información general",
                "tools_needed": ["RAG_SEARCH"],
                "reasoning": "Consulta general, usar RAG",
                "requires_additional_info": False
            }
    
    @traceable(name="OrchestratorAgent.execute_tools")
    def execute_tools(self, analysis: dict, query: str, trace_id: str = None) -> dict:
        """
        Ejecutar las herramientas necesarias según el análisis.
        
        Args:
            analysis: Resultado del análisis de reasoning
            query: Consulta original del usuario
            trace_id: ID del trace para agrupar logs
            
        Returns:
            dict: Resultados de las herramientas
        """
        tools_used = analysis.get("tools_needed", [])
        results = {
            "tools_used": tools_used,
            "data": {}
        }
        
        for tool in tools_used:
            try:
                # Log inicio de ejecución de herramienta
                tracer.log(
                    operation=f"{tool}_START",
                    message=f"Iniciando ejecución de {tool}",
                    metadata={"query": query[:100]},
                    level="INFO",
                    trace_id=trace_id
                )
                
                if tool == "RAG_SEARCH":
                    tool_result = self._execute_rag_search(query, trace_id)
                    results["data"]["rag_search"] = tool_result
                
                elif tool == "PRODUCT_SEARCH":
                    tool_result = self._execute_product_search(query, trace_id)
                    results["data"]["product_search"] = tool_result
                
                elif tool == "TICKET_CREATE":
                    tool_result = self._execute_ticket_create(query, trace_id)
                    results["data"]["ticket_create"] = tool_result
                
                elif tool == "TICKET_QUERY":
                    tool_result = self._execute_ticket_query(query, trace_id)
                    results["data"]["ticket_query"] = tool_result
                
                else:
                    tool_result = {"error": "Herramienta no implementada"}
                    results["data"][tool] = tool_result
                
                # Log éxito de herramienta
                tracer.log(
                    operation=f"{tool}_SUCCESS",
                    message=f"Herramienta {tool} ejecutada exitosamente",
                    metadata={"method": tool_result.get("method", "N/A")},
                    level="SUCCESS",
                    trace_id=trace_id
                )
                    
            except Exception as e:
                tracer.log(
                    operation="TOOL_EXECUTION_ERROR",
                    message=f"Error ejecutando {tool}: {str(e)}",
                    level="ERROR",
                    trace_id=trace_id
                )
                results["data"][tool] = {"error": str(e)}
        
        return results
    
    def _execute_rag_search(self, query: str, trace_id: str = None) -> dict:
        """Ejecutar búsqueda RAG usando el RAG Agent"""
        response = self.rag_agent.process_query(query, enable_logging=False, trace_id=trace_id)
        return {
            "result": response,
            "method": "RAG search in documents"
        }
    
    def _execute_product_search(self, query: str, trace_id: str = None) -> dict:
        """Ejecutar búsqueda de productos usando el RAG Agent"""
        query_info = self.rag_agent.query_processor.classify_query(query)
        response = self.rag_agent._handle_product_query(query, query_info, enable_logging=False, trace_id=trace_id)
        return {
            "result": response,
            "method": "Product search in inventory"
        }
    
    def _execute_ticket_create(self, query: str, trace_id: str = None) -> dict:
        """Ejecutar creación de ticket usando el RAG Agent"""
        query_info = self.rag_agent.query_processor.classify_query(query)
        response = self.rag_agent._handle_ticket_query(query, query_info, enable_logging=False, trace_id=trace_id)
        return {
            "result": response,
            "method": "Ticket creation"
        }
    
    def _execute_ticket_query(self, query: str, trace_id: str = None) -> dict:
        """Ejecutar consulta de ticket usando el RAG Agent"""
        query_info = self.rag_agent.query_processor.classify_query(query)
        response = self.rag_agent._handle_consulta_ticket(query, query_info, trace_id=trace_id)
        return {
            "result": response,
            "method": "Ticket query"
        }
    
    @traceable(name="OrchestratorAgent.store_user_info")
    def store_user_info(self, session_id: str, query: str, trace_id: str = None) -> dict:
        """
        Extraer y almacenar información del usuario de la consulta
        
        Args:
            session_id: ID de la sesión
            query: Consulta del usuario
            trace_id: ID del trace
            
        Returns:
            dict: Información extraída
        """
        try:
            from tools.chat_memory import extract_user_info as extract_info_helper
            
            # Llamar a la función helper que internamente llama store_chat_memory con trace_id
            info = extract_info_helper(query, session_id, trace_id=trace_id)
            
            tracer.log(
                operation="USER_INFO_EXTRACTED",
                message=f"Información extraída: {len(info.get('extracted', {}))} campo(s)",
                metadata=info,
                level="INFO",
                trace_id=trace_id
            )
            
            return info
            
        except Exception as e:
            tracer.log(
                operation="EXTRACT_INFO_ERROR",
                message=f"Error extrayendo info: {str(e)}",
                level="ERROR",
                trace_id=trace_id
            )
            return {"session_id": session_id, "extracted": {}, "count": 0}
    
    @traceable(name="OrchestratorAgent.retrieve_memory")
    def retrieve_memory(self, session_id: str, trace_id: str = None) -> str:
        """
        Recuperar memorias de la sesión para enriquecer el contexto
        
        Args:
            session_id: ID de la sesión
            trace_id: ID del trace
            
        Returns:
            str: Contexto formateado
        """
        try:
            memories = retrieve_chat_memory(session_id, memory_key=None, trace_id=trace_id)
            
            if memories.get("found"):
                context = get_context_for_query(session_id, trace_id=trace_id)
                
                tracer.log(
                    operation="MEMORY_RETRIEVED",
                    message=f"Memorias recuperadas para sesión",
                    metadata={"session_id": session_id, "count": memories.get("count", 0)},
                    level="INFO",
                    trace_id=trace_id
                )
                
                return context
            else:
                return ""
                
        except Exception as e:
            tracer.log(
                operation="MEMORY_RETRIEVE_ERROR",
                message=f"Error recuperando memoria: {str(e)}",
                level="ERROR",
                trace_id=trace_id
            )
            return ""


# Singleton global
_orchestrator_instance = None

def get_orchestrator():
    """Obtener instancia global del orquestador"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = OrchestratorAgent()
    return _orchestrator_instance

