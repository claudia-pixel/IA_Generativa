"""
Herramienta para procesar consultas y clasificarlas
"""

import os
import sys
from typing import Dict, Any, List

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.tracing import tracer

# Importar traceable para LangSmith
try:
    from langsmith import traceable
except ImportError:
    # Si no está disponible, usar decorador vacío
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class QueryProcessor:
    """
    Herramienta para procesar y clasificar consultas del usuario
    """
    
    # Categorías de consultas
    CATEGORIES = {
        "producto": ["producto", "productos", "inventario", "catálogo", "disponibilidad", "stock"],
        "precio": ["precio", "costo", "cuánto cuesta", "valor"],
        "contacto": ["teléfono", "whatsapp", "email", "contactar", "contacto"],
        "devolución": ["devolución", "devolver", "reembolso", "garantía", "cambio"],
        "envío": ["envío", "entrega", "shipping", "transporte", "días"],
        "general": ["información", "ayuda", "duda", "consulta"]
    }
    
    # Palabras clave para consultas de lista
    LIST_KEYWORDS = [
        "lista", "listado", "todos", "cuáles", "qué", "muéstrame",
        "selección", "opciones", "categorías"
    ]
    
    def __init__(self):
        """Inicializar el procesador de consultas"""
        self.query_history: List[str] = []
    
    @traceable(name="QueryProcessor.classify_query")
    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Clasificar una consulta del usuario
        
        Args:
            query (str): Consulta del usuario
            
        Returns:
            dict: Información clasificada sobre la consulta
        """
        query_lower = query.lower()
        
        # Detectar categoría
        category = self._detect_category(query_lower)
        
        # Detectar tipo de consulta (lista vs específica)
        is_list_query = self._is_list_query(query_lower)
        
        # Detectar urgencia
        urgency = self._detect_urgency(query_lower)
        
        # Detectar intención
        intention = self._detect_intention(query_lower)
        
        classification = {
            "category": category,
            "is_list_query": is_list_query,
            "urgency": urgency,
            "intention": intention,
            "original_query": query,
            "processed_query": query_lower
        }
        
        # Agregar al historial
        self.query_history.append(query)
        
        # Log para trazabilidad
        tracer.log(
            operation="QUERY_CLASSIFICATION",
            message=f"Consulta clasificada: {category}",
            metadata=classification,
            level="INFO"
        )
        
        return classification
    
    def _detect_category(self, query: str) -> str:
        """Detectar la categoría de la consulta"""
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in query for keyword in keywords):
                return category
        return "general"
    
    def _is_list_query(self, query: str) -> bool:
        """Detectar si la consulta pide una lista de elementos"""
        return any(keyword in query for keyword in self.LIST_KEYWORDS)
    
    def _detect_urgency(self, query: str) -> str:
        """Detectar el nivel de urgencia de la consulta"""
        urgent_keywords = ["urgente", "ya", "inmediato", "ahora"]
        high_keywords = ["importante", "necesito", "requiero"]
        
        if any(keyword in query for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in query for keyword in high_keywords):
            return "high"
        else:
            return "normal"
    
    def _detect_intention(self, query: str) -> str:
        """Detectar la intención del usuario"""
        if any(word in query for word in ["quiero", "deseo", "busco", "necesito"]):
            return "buy"
        elif any(word in query for word in ["tengo", "mi pedido", "mi compra"]):
            return "track"
        elif any(word in query for word in ["problema", "error", "no funciona"]):
            return "support"
        elif any(word in query for word in ["información", "qué es", "cuál es"]):
            return "info"
        else:
            return "general"
    
    def extract_entities(self, query: str) -> List[Dict[str, str]]:
        """
        Extraer entidades relevantes de la consulta
        
        Args:
            query (str): Consulta del usuario
            
        Returns:
            list: Lista de entidades extraídas
        """
        entities = []
        
        # Productos (patrones comunes)
        # Esto es un ejemplo básico, podrías usar NER más avanzado
        if any(word in query.lower() for word in ["botella", "bolsa", "cepillo", "cargador"]):
            entities.append({
                "type": "product",
                "value": query
            })
        
        # Números (precios, cantidades)
        import re
        numbers = re.findall(r'\d+\.?\d*', query)
        for num in numbers:
            entities.append({
                "type": "number",
                "value": num
            })
        
        return entities
    
    def generate_search_queries(self, query: str) -> List[str]:
        """
        Generar múltiples variaciones de consulta para mejor búsqueda
        
        Args:
            query (str): Consulta original
            
        Returns:
            list: Lista de variaciones de la consulta
        """
        variations = [query]  # La consulta original
        
        # Agregar variaciones si es una consulta de lista
        if self._is_list_query(query.lower()):
            variations.extend([
                f"{query} con precios",
                f"{query} disponibles",
                f"productos relacionados con {query}"
            ])
        
        # Agregar variación con sinónimos comunes
        variations.append(query.replace("cuánto cuesta", "precio de"))
        variations.append(query.replace("qué productos", "catálogo"))
        
        return variations

