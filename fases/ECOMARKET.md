**ECOMARKET**

**Documentación del Sistema RAG para Atención al Cliente – EcoMarket**

**Fase 1: Selección de Componentes del Sistema RAG**

**🔹 Modelo de Embeddings seleccionado:**   
Se utilizó **OpenAI Embeddings** (text-embedding-ada-002) para generar representaciones semánticas precisas en español. Este modelo fue elegido por su alta calidad en embeddings multilingües, aunque requiere API key de OpenAI. El modelo genera vectores de 1536 dimensiones.

**🔹 Base de datos vectorial utilizada:**   
Se empleó **ChromaDB**, una base de datos vectorial moderna y eficiente. Se eligió por su facilidad de integración con LangChain, persistencia automática en disco, y excelente rendimiento para búsquedas por similitud. La base se almacena en `./static/persist/` con el nombre de colección `sample_documents`.

**Fase 2: Creación de la Base de Conocimiento**

**🔹 Documentos utilizados:**

| **Tipo de documento** | **Archivo**                        | **Contenido**                                       |
|-----------------------|------------------------------------|-----------------------------------------------------|
| TXT                   | politica_devoluciones.txt          | Normativa de reembolsos y condiciones de devolución |
| Excel                 | Inventario_Sostenible.xlsx         | Información de productos, stock y precios           |
| TXT                   | preguntas_frecuentes.txt           | Preguntas frecuentes de clientes                    |

**🔹 Estrategia de segmentación (chunking):**   
Se implementó una **estrategia de chunking adaptativa** que ajusta automáticamente los parámetros según el tipo de contenido:

- **Datos estructurados** (Excel, CSV): `chunk_size=300`, `chunk_overlap=30`
- **Texto narrativo** (TXT, PDF): `chunk_size=500`, `chunk_overlap=50`

Esta técnica optimiza la recuperación contextual para diferentes tipos de documentos, mejorando la precisión del sistema RAG.

**🔹 Indexación:**   
Los documentos fueron convertidos en vectores mediante OpenAI Embeddings y almacenados en ChromaDB. Se generó una colección llamada `sample_documents` que permite búsquedas rápidas y precisas con persistencia automática.

**Fase 3: Integración y Ejecución del Código**

**🔹 Entorno de trabajo:**   
Aplicación web desarrollada con **Streamlit** y desplegada en **Docker**. El sistema incluye:
- Interfaz web moderna con temas personalizables
- Panel de administración para gestión de documentos
- Sistema de autenticación
- Base de datos SQLite para metadatos
- API REST para operaciones CRUD

**🔹 Carga de documentos:**   
Se utilizaron loaders especializados de LangChain para cada tipo de archivo:
- `TextLoader` para archivos .txt
- `load_excel_with_pandas()` para archivos Excel (con pandas)
- `PyPDFLoader` para PDFs
- `Docx2txtLoader` para documentos Word

Los datos se procesan automáticamente y se registran en la base de datos SQLite.

**🔹 Construcción del pipeline RAG:**   
Se integró **GPT-4o-mini** de OpenAI como LLM principal con configuración optimizada:
- `temperature=0.1` para respuestas más precisas
- `max_tokens=500` para respuestas concisas
- Prompts mejorados para evitar alucinaciones
- Retriever configurado con `k=5` documentos

**🔹 Características avanzadas implementadas:**
- **Chunking adaptativo** basado en el tipo de contenido
- **Prompts especializados** para información de contacto
- **Detección inteligente** de consultas específicas
- **Logging detallado** para debugging
- **Manejo robusto de errores** y reintentos
- **Configuración de base de datos optimizada** (WAL mode)

**🔹 Pruebas del sistema:**   
Se realizaron consultas típicas de atención al cliente, incluyendo:
- Disponibilidad y precios de productos específicos
- Información de contacto exacta (teléfonos, emails, WhatsApp)
- Políticas de devolución y condiciones
- Preguntas frecuentes

El sistema responde con información **exacta** extraída de los documentos, evitando alucinaciones mediante prompts estrictos y configuración optimizada del LLM.

**🔹 Arquitectura del sistema:**
```
Frontend (Streamlit) → Backend (Python) → ChromaDB (Vectores) + SQLite (Metadatos)
                                    ↓
                              OpenAI API (Embeddings + LLM)
```

**🔹 Despliegue:**
- **Docker Compose** para orquestación de servicios
- **Nginx** como proxy reverso
- **Volúmenes persistentes** para datos
- **Variables de entorno** para configuración
- **Inicialización automática** de documentos de muestra
