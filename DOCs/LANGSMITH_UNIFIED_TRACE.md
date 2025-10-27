# Trazas Unificadas en LangSmith

## 🎯 Problema Resuelto

Las funciones decoradas con `@traceable` estaban creando trazas separadas en LangSmith. Ahora todas las trazas se agrupan bajo un único parent run.

## 🔧 Solución Implementada

### Context Manager de LangSmith

```python
# src/agents/intelligent_agent.py

def process_query(self, query, enable_logging=False):
    trace_id = tracer.generate_trace_id()
    
    # Context manager envuelve TODA la ejecución
    if LANGSMITH_AVAILABLE and trace:
        with trace(name=f"EcoMarketAgent - {trace_id}", 
                   metadata={"user_query": query[:200], "trace_id": trace_id}) as ls_trace:
            return self._process_with_langsmith(query, trace_id, start_time, ls_trace.run_id)
    else:
        return self._process_without_langsmith(query, trace_id, start_time)
```

## 📊 Estructura de Trazas

### Antes (Trazas Separadas)

```
❌ check_product_existence (trace separada)
❌ QueryProcessor.classify_query (trace separada)  
❌ RunnableSequence (trace separada)
```

### Después (Traza Unificada)

```
✅ EcoMarketAgent - trace_8f3a5d2e1c4b (parent run)
   ├─ check_product_existence (child run)
   ├─ QueryProcessor.classify_query (child run)
   ├─ RunnableSequence (child run)
   └─ ... todas agrupadas
```

## 🔍 Cómo Funciona

1. **IntelligentAgent** genera `trace_id` único
2. **Context Manager** `trace()` envuelve toda la ejecución
3. Todos los decoradores `@traceable` dentro del contexto se agrupan automáticamente
4. Las trazas de tools, queries, etc. aparecen como child runs

## 📋 Archivos Actualizados

- ✅ `src/agents/intelligent_agent.py` - Context manager de LangSmith
- ✅ Import de `langsmith.trace` para contexto
- ✅ Métodos `_process_with_langsmith` y `_process_without_langsmith`

## 🎨 Resultado en LangSmith

Al ver una traza en LangSmith:

```
EcoMarketAgent - trace_8f3a5d2e1c4b
├─ LLM_REASONING (si aplica)
├─ check_product_existence
│  ├─ Input: "producto"
│  ├─ Result: {...}
│  └─ Duration: 3.27s
├─ QueryProcessor.classify_query
│  ├─ Input: "query"
│  ├─ Output: "categoria"
│  └─ Duration: 0.00s
├─ RunnableSequence
│  ├─ Retrieval
│  ├─ Generation
│  └─ Duration: 2.45s
└─ Total Duration: ~8s
```

## ✅ Beneficios

1. **Visibilidad Completa**: Ver toda la interacción en un solo lugar
2. **Debugging Más Fácil**: Identificar dónde falló la consulta
3. **Performance Tracking**: Medir tiempos por componente
4. **Agrupación Intuitiva**: Todas las operaciones relacionadas juntas

## 🚀 Uso

El sistema funciona automáticamente. Al hacer una consulta:

1. Se genera un `trace_id` único
2. Se crea un context manager de LangSmith
3. Todas las operaciones dentro se agrupan
4. Se ven todas juntas en el panel de LangSmith

## 📊 Logs Locales vs LangSmith

### Logs Locales (`tracer.log()`)
- Se agrupan por `trace_id`
- Disponibles en el panel de admin
- Útiles para debugging local

### LangSmith Traces
- Se agrupan por context manager
- Disponibles en el dashboard de LangSmith
- Útiles para análisis avanzado

## 🔧 Configuración

Requiere variables de entorno:
```bash
LANGSMITH_TRACING=true
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=...
```

## 📝 Notas

- El context manager captura automáticamente todas las trazas dentro
- Los decoradores `@traceable` dentro se agrupan
- El `run_id` del parent se pasa como metadata
- Si LangSmith no está disponible, se usa el flujo sin agrupación

