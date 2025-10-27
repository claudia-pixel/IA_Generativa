"""
Agente RAG para el sistema de EcoMarket
Maneja la lógica de recuperación y generación de respuestas
"""

import os
import sys
import time
import re

# Agregar src al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.vector_functions import (
    load_retriever,
    get_combined_retriever,
    generate_answer_from_context
)
from utils.tracing import tracer, log_retrieval, log_generation
from tools.document_retriever import DocumentRetriever
from tools.query_processor import QueryProcessor
from tools.product_checker import check_product_existence

# Importar traceable para unificar trazas
try:
    from langsmith import traceable
    from contextlib import nullcontext
    TRACEABLE_AVAILABLE = True
except ImportError:
    # Si no está disponible, crear decorador vacío
    def traceable(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    from contextlib import nullcontext
    TRACEABLE_AVAILABLE = False


class EcoMarketAgent:
    """
    Agente RAG para responder consultas de clientes usando documentos internos
    """
    
    def __init__(self):
        """Inicializar el agente RAG"""
        self.retriever = None
        self.initialized = False
        
        # Inicializar herramientas
        self.document_retriever = DocumentRetriever()
        self.query_processor = QueryProcessor()
        
        self._initialize()
    
    def _initialize(self):
        """Inicializar el retriever"""
        try:
            # Verificar si existe la base de datos ChromaDB
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            chroma_path = os.path.join(base_dir, "static/persist/chroma.sqlite3")
            
            if os.path.exists(chroma_path):
                self.retriever = get_combined_retriever()
                self.initialized = True
                tracer.log(
                    operation="AGENT_INITIALIZATION",
                    message="Agente RAG inicializado exitosamente",
                    metadata={"initialized": True},
                    level="SUCCESS"
                )
            else:
                self.initialized = False
                tracer.log(
                    operation="AGENT_INITIALIZATION",
                    message="Base de datos vectorial no encontrada",
                    metadata={"chroma_path": chroma_path},
                    level="WARNING"
                )
        except Exception as e:
            self.initialized = False
            tracer.log(
                operation="AGENT_INITIALIZATION",
                message=f"Error inicializando agente: {str(e)}",
                metadata={"error": str(e)},
                level="ERROR"
            )
    
    def is_ready(self):
        """Verificar si el agente está listo para responder"""
        return self.initialized and self.retriever is not None
    
    @traceable(name="EcoMarketAgent.process_query")
    def process_query(self, question: str, enable_logging: bool = False) -> str:
        """
        Procesar una consulta del usuario usando herramientas
        
        Args:
            question (str): Pregunta del usuario
            enable_logging (bool): Habilitar logging detallado
            
        Returns:
            str: Respuesta del agente
        """
        if not self.is_ready():
            return self._get_fallback_response()
        
        try:
            # Paso 1: Clasificar la consulta
            query_info = self.query_processor.classify_query(question)
            
            tracer.log(
                operation="AGENT_PROCESSING",
                message=f"Procesando consulta tipo: {query_info['category']}",
                metadata=query_info,
                level="INFO"
            )
            
            # Paso 2: Detectar si es consulta de producto
            if self._is_product_query(question, query_info):
                response = self._handle_product_query(question, query_info, enable_logging)
                return response
            
            # Paso 3: Si es una consulta de lista, detectar si es sobre productos
            if query_info['is_list_query']:
                # Verificar si es lista de productos o lista general
                if self._is_product_list_query(question, query_info):
                    # Usar herramienta de verificación de productos
                    response = self._handle_product_query(question, query_info, enable_logging)
                else:
                    # Usar estrategia de lista general (RAG estándar)
                    response = self._handle_list_query(question, query_info, enable_logging)
            else:
                # Paso 4: Usar estrategia estándar con herramientas
                response = self._handle_standard_query(question, query_info, enable_logging)
            
            return response
            
        except Exception as e:
            tracer.log(
                operation="RAG_ERROR",
                message=f"Error procesando consulta: {str(e)}",
                metadata={"question": question[:100], "error": str(e)},
                level="ERROR"
            )
            
            return self._get_error_response(str(e))
    
    def _handle_list_query(self, question: str, query_info: dict, enable_logging: bool) -> str:
        """Manejar consultas que solicitan listas de productos"""
        # Generar múltiples variaciones de la consulta
        queries = self.query_processor.generate_search_queries(question)
        
        # Recuperar documentos para cada variación
        all_documents = []
        for query_variant in queries:
            docs = self.document_retriever.search(query_variant)
            all_documents.extend(docs)
        
        # Generar respuesta con el contexto ampliado
        response = generate_answer_from_context(
            self.retriever,
            question,
            enable_logging=enable_logging
        )
        
        return response
    
    def _handle_standard_query(self, question: str, query_info: dict, enable_logging: bool) -> str:
        """Manejar consultas estándar"""
        # Buscar documentos relevantes
        search_results = self.document_retriever.search(question)
        
        # Generar respuesta usando RAG estándar
        response = generate_answer_from_context(
            self.retriever,
            question,
            enable_logging=enable_logging
        )
        
        return response
    
    def _is_product_query(self, question: str, query_info: dict) -> bool:
        """Detectar si la consulta es sobre productos específicos"""
        question_lower = question.lower()
        
        # Palabras clave que indican consultas de producto
        product_keywords = [
            "¿tienen", "¿tienes", "¿hay", "¿existe", "¿disponible",
            "producto", "productos", "catalogo", "catálogo", "inventario",
            "en stock", "disponibilidad", "busco", "necesito", "quiero",
            "por categoria", "por categoría", "menos de", "menor a",
            "mayor a", "más de", "precio"
        ]
        
        # Si es categoría producto o contiene keywords
        is_product = query_info.get('category') == 'producto'
        has_keywords = any(keyword in question_lower for keyword in product_keywords)
        
        return is_product or has_keywords
    
    def _is_product_list_query(self, question: str, query_info: dict) -> bool:
        """Detectar si una consulta de lista es sobre productos específicos"""
        question_lower = question.lower()
        
        # Palabras clave específicas de productos
        product_keywords = [
            "producto", "productos", "catalogo", "catálogo", "inventario",
            "en stock", "disponibilidad", "busco", "necesito", "quiero",
            "categoría", "categoria", "precio", "stock", "disponible"
        ]
        
        # Verificar si es categoría producto
        is_product_category = query_info.get('category') == 'producto'
        
        # Verificar keywords de productos
        has_product_keywords = any(keyword in question_lower for keyword in product_keywords)
        
        return is_product_category or has_product_keywords
    
    def _handle_product_query(self, question: str, query_info: dict, enable_logging: bool) -> str:
        """Manejar consultas de productos usando la herramienta de verificación"""
        try:
            question_lower = question.lower()
            
            # Determinar tipo de búsqueda
            search_type = "producto"
            categoria_filtro = None
            precio_min = None
            precio_max = None
            
            # Extraer categoría del filtro si existe
            # Primero verificar si pregunta por categorías disponibles (pregunta sobre categorías, no filtro)
            is_asking_about_categories = (
                "qué categor" in question_lower or 
                "que categor" in question_lower or
                "cuales categor" in question_lower or
                "cuáles categor" in question_lower or
                "que tipos" in question_lower or
                "qué tipos" in question_lower
            )
            
            if "categoría" in question_lower or "categoria" in question_lower and not is_asking_about_categories:
                # Buscar palabra después de "categoría" o "de"
                categoria_match = re.search(r'(?:categoría|categoria|de)\s+(\w+)', question_lower)
                if categoria_match:
                    categoria_filtro = categoria_match.group(1).title()
                    search_type = "categoria"
            
            # Si pregunta sobre categorías disponibles, usar búsqueda especial
            if is_asking_about_categories:
                search_type = "todas_categorias"
            
            # Extraer rango de precio
            precio_matches = re.findall(r'(\d+(?:\.\d+)?)', question)
            if precio_matches:
                if "menos de" in question_lower or "menor a" in question_lower:
                    precio_max = float(precio_matches[0])
                elif "más de" in question_lower or "mayor a" in question_lower:
                    precio_min = float(precio_matches[0])
            
            # Detectar si es búsqueda de lista (productos separados por comas, "y", o preguntas de lista)
            is_list_query = (
                "lista" in question_lower or 
                "cuáles" in question_lower or
                "qué productos" in question_lower or
                "muestra" in question_lower or
                query_info.get('is_list_query')
            )
            
            # Detectar si es solicitud de TODOS los productos disponibles
            is_all_products_query = (
                "todos los productos" in question_lower or
                "todos tus productos" in question_lower or
                "todos productos" in question_lower or
                "catálogo completo" in question_lower or
                ("lista" in question_lower and "disponibles" in question_lower) or
                ("lista" in question_lower and "tienes" in question_lower) or
                ("qué productos" in question_lower and "tienes" in question_lower)
            )
            
            # También detectar si hay múltiples productos separados por comas o "y"
            has_multiple_products = (
                question.count(',') > 0 or 
                (question.count(' y ') > 0 or question.count(' y ') > 0)
            )
            
            # Si es solicitud de todos los productos
            if is_all_products_query:
                search_type = "todos_productos"
            # Si es lista de productos específicos
            elif is_list_query and has_multiple_products:
                search_type = "lista"
            elif is_list_query:
                # Si es pregunta de lista sin productos específicos, también retornar todos
                search_type = "todos_productos"
            
            # Ejecutar búsqueda de producto
            result = check_product_existence(
                query=question,
                search_type=search_type,
                categoria_filtro=categoria_filtro,
                precio_min=precio_min,
                precio_max=precio_max,
                umbral_similitud=0.7
            )
            
            # Formatear respuesta según el tipo de resultado
            if search_type == "producto":
                response = self._format_single_product_response(result)
            elif search_type == "lista":
                response = self._format_list_product_response(result)
            elif search_type == "categoria":
                response = self._format_category_response(result)
            elif search_type == "todas_categorias":
                response = self._format_all_categories_response(result)
            elif search_type == "todos_productos":
                response = self._format_all_products_response(result)
            else:
                # Respuesta estándar con RAG
                response = generate_answer_from_context(
                    self.retriever,
                    question,
                    enable_logging=enable_logging
                )
            
            tracer.log(
                operation="PRODUCT_QUERY",
                message=f"Consulta de producto procesada: {search_type}",
                metadata={"search_type": search_type, "result": result},
                level="INFO"
            )
            
            return response
            
        except Exception as e:
            tracer.log(
                operation="PRODUCT_QUERY_ERROR",
                message=f"Error en consulta de producto: {str(e)}",
                level="ERROR"
            )
            # Fallback a RAG estándar
            return generate_answer_from_context(
                self.retriever,
                question,
                enable_logging=enable_logging
            )
    
    def _format_single_product_response(self, result: dict) -> str:
        """Formatear respuesta para un producto individual"""
        if result.get('existe'):
            nombre = result.get('producto_nombre', 'Producto')
            categoria = result.get('categoria', 'N/A')
            cantidad = result.get('cantidad', 'N/A')
            precio = result.get('precio', 'N/A')
            
            response = f"""
✅ **Producto Encontrado:**

📦 **{nombre}**
- Categoría: {categoria}
- Cantidad en Stock: {cantidad} unidades
- Precio: ${precio}

¿Te gustaría más información sobre este producto?
"""
            
            # Agregar matches alternativos si existen
            if result.get('matches_alternativos'):
                response += "\n\n📋 **Productos alternativos similares:**\n"
                for alt in result['matches_alternativos'][:3]:  # Máximo 3 alternativas
                    response += f"- {alt['producto_nombre']} (Categoría: {alt['categoria']}, Precio: ${alt['precio']})\n"
            
            return response
        else:
            return f"""
❌ **Producto no encontrado**

No encontramos el producto que buscas en nuestro inventario.

¿Podrías intentar con:
- Otro nombre o descripción
- Buscar por categoría
- O contactarnos directamente:
  📧 soporte@ecomarket.com
  📞 +57 324 456 4450
"""
    
    def _format_list_product_response(self, result: dict) -> str:
        """Formatear respuesta para lista de productos"""
        resultados = result.get('resultados', [])
        total_encontrados = result.get('total_encontrados', 0)
        total_buscados = result.get('total_buscados', 0)
        
        if total_encontrados == 0:
            return """
❌ **No se encontraron productos**

No se encontraron productos en nuestro inventario.

¿Podrías intentar con otros términos de búsqueda?
"""
        
        response = f"""
📋 **Resultados de Búsqueda:**

Encontrados {total_encontrados} de {total_buscados} productos buscados:

"""
        for idx, producto in enumerate(resultados, 1):
            if producto.get('existe'):
                det = producto.get('detalles_match', {})
                response += f"{idx}. ✅ **{producto.get('producto_ingresado')}**\n"
                response += f"   → {det.get('producto_nombre', 'Producto encontrado')}\n"
                response += f"   - Categoría: {det.get('categoria', 'N/A')}\n"
                response += f"   - Stock: {det.get('cantidad', 'N/A')}\n"
                response += f"   - Precio: ${det.get('precio', 'N/A')}\n\n"
            else:
                response += f"{idx}. ❌ **{producto.get('producto_ingresado')}** (No encontrado)\n\n"
        
        return response
    
    def _format_category_response(self, result: dict) -> str:
        """Formatear respuesta para búsqueda por categoría"""
        productos = result.get('productos', [])
        total = result.get('total', 0)
        categoria = result.get('categoria', 'Productos')
        
        if total == 0:
            return f"""
❌ **No se encontraron productos**

No hay productos en la categoría '{categoria}' actualmente disponibles.
"""
        
        response = f"""
📦 **Productos en categoría: {categoria}**

Encontrados {total} productos:

"""
        for idx, producto in enumerate(productos, 1):
            response += f"{idx}. **{producto.get('nombre', 'Producto')}**\n"
            response += f"   - Stock: {producto.get('cantidad', 'N/A')} unidades\n"
            response += f"   - Precio: ${producto.get('precio', 'N/A')}\n\n"
        
        return response
    
    def _format_all_categories_response(self, result: dict) -> str:
        """Formatear respuesta para listar todas las categorías disponibles"""
        categorias = result.get('categorias', [])
        total = result.get('total', 0)
        
        if total == 0:
            return """
❌ **No se encontraron categorías**

No hay categorías disponibles en nuestro inventario actual.
"""
        
        response = """
📦 **Categorías Disponibles:**

Tienes {total} categorías de productos:

""".format(total=total)
        
        for idx, cat in enumerate(categorias, 1):
            cat_name = cat.get('categoria', 'Sin categoría')
            cat_count = cat.get('cantidad_productos', 0)
            response += f"{idx}. **{cat_name}** ({cat_count} productos)\n"
        
        response += "\n💡 *Pregúntame por productos de una categoría específica para ver más detalles*"
        
        return response
    
    def _format_all_products_response(self, result: dict) -> str:
        """Formatear respuesta para listar todos los productos disponibles"""
        productos = result.get('productos', [])
        total = result.get('total', 0)
        
        if total == 0:
            return """
❌ **No se encontraron productos**

No hay productos disponibles en nuestro inventario actual.
"""
        
        response = f"""
📦 **Catálogo Completo - {total} Productos Disponibles**

"""
        
        # Agrupar por categoría para mejor visualización
        por_categoria = {}
        for producto in productos:
            categoria = producto.get('categoria', 'Sin categoría')
            if categoria not in por_categoria:
                por_categoria[categoria] = []
            por_categoria[categoria].append(producto)
        
        # Formatear por categorías
        for idx, (categoria, prods) in enumerate(por_categoria.items(), 1):
            response += f"\n### {categoria} ({len(prods)} productos)\n\n"
            
            for prod in prods:
                nombre = prod.get('nombre', 'Producto')
                cantidad = prod.get('cantidad', 'N/A')
                precio = prod.get('precio', 'N/A')
                
                # Mostrar como lista numerada
                response += f"**{nombre}**\n"
                response += f"- Stock: {cantidad} unidades\n"
                response += f"- Precio: ${precio}\n\n"
        
        response += "\n💡 *¿Te interesa algún producto en particular? Pregúntame por más detalles*"
        
        return response
    
    def _get_fallback_response(self) -> str:
        """Obtener respuesta de respaldo cuando el agente no está disponible"""
        return """
        🙏 Disculpa, actualmente estamos configurando nuestro sistema de respuestas automáticas.
        
        Por favor, contacta directamente con nuestro equipo de soporte:
        - 📧 Email: soporte@ecomarket.com
        - 📞 Teléfono: +57 324 456 4450
        - ⏰ Horario: Lunes a Viernes 9:00 AM - 6:00 PM
        """
    
    def _get_error_response(self, error_msg: str) -> str:
        """Obtener respuesta de error"""
        return """
        😔 Lo siento, tuve un problema al procesar tu consulta.
        
        Por favor, intenta nuevamente o contacta a nuestro equipo:
        - 📧 soporte@ecomarket.com
        - 📞 +57 324 456 4450
        """
    
    def get_system_status(self) -> dict:
        """Obtener estado del sistema del agente"""
        status = {
            "initialized": self.initialized,
            "ready": self.is_ready(),
            "retriever_available": self.retriever is not None
        }
        
        # Agregar información adicional si está disponible
        if self.is_ready():
            status["status"] = "operational"
            status["message"] = "Agente listo para responder consultas"
        else:
            status["status"] = "not_initialized"
            status["message"] = "Agente no puede responder - base de datos no disponible"
        
        return status

# Instancia global del agente (singleton)
_agent_instance = None

def get_agent() -> EcoMarketAgent:
    """Obtener instancia global del agente (singleton pattern)"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = EcoMarketAgent()
    return _agent_instance

