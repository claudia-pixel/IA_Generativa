# 🌿 EcoMarket RAG System

**Sistema RAG para Atención al Cliente – EcoMarket**

Este proyecto implementa un sistema de generación aumentada por recuperación (RAG) para mejorar la atención al cliente de EcoMarket, una empresa de e-commerce sostenible. El sistema permite responder preguntas frecuentes y consultas sobre productos utilizando documentos internos como fuente confiable.

## 👥 Integrantes

- Claudia Martinez
- Mario Castellanos  
- Enrique Manzano

## 🎯 Objetivos del Proyecto

- Integrar un modelo de lenguaje con recuperación semántica para responder consultas reales de clientes
- Utilizar documentos internos (TXT, Excel, PDF) como base de conocimiento
- Evaluar la precisión, transparencia y ética del sistema en un entorno educativo
- Implementar una interfaz web moderna y fácil de usar

## 🏗️ Arquitectura del Sistema

```
Frontend (Streamlit) → Backend (Python) → ChromaDB (Vectores) + SQLite (Metadatos)
                                    ↓
                              OpenAI API (Embeddings + LLM)
```

## 🔧 Componentes del Sistema

| **Componente** | **Herramienta elegida** | **Justificación** |
|----------------|-------------------------|-------------------|
| **Embeddings** | OpenAI Embeddings (text-embedding-ada-002) | Alta calidad multilingüe, 1536 dimensiones |
| **Vector DB** | ChromaDB | Persistencia automática, integración con LangChain |
| **LLM** | GPT-4o-mini | Respuestas precisas, configuración optimizada |
| **Framework** | LangChain | Modular, flexible y orientado a sistemas RAG |
| **Frontend** | Streamlit | Interfaz web moderna y responsiva |
| **Backend** | Python + FastAPI | API REST robusta y escalable |
| **Base de Datos** | SQLite | Metadatos y gestión de documentos |
| **Despliegue** | Docker + Nginx | Contenedorización y proxy reverso |

## 📚 Documentos Utilizados

| **Tipo** | **Archivo** | **Contenido** |
|----------|-------------|---------------|
| TXT | `politica_devoluciones.txt` | Normativa de reembolsos y condiciones |
| Excel | `Inventario_Sostenible.xlsx` | Productos, stock y precios |
| TXT | `preguntas_frecuentes.txt` | Preguntas frecuentes de clientes |

## 🧠 Estrategia de Chunking Adaptativa

- **Datos estructurados** (Excel, CSV): `chunk_size=300`, `chunk_overlap=30`
- **Texto narrativo** (TXT, PDF): `chunk_size=500`, `chunk_overlap=50`

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Docker y Docker Compose
- Git
- API Key de OpenAI

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd GENERATIVE_AI_ICESI
```

### 2. Configurar Variables de Entorno

```bash
cp env.example .env
```

Editar el archivo `.env` y agregar tu API key de OpenAI:

```env
OPENAI_API_KEY=tu_api_key_aqui
DOCKER_CONTAINER=true
```

### 3. Ejecutar con Docker (Recomendado)

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# O ejecutar en segundo plano
docker-compose up -d --build
```

La aplicación estará disponible en: `http://localhost:8501`

### 4. Ejecutar Localmente (Desarrollo)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export OPENAI_API_KEY=tu_api_key_aqui

# Inicializar la aplicación
python init_app.py

# Ejecutar la aplicación
streamlit run app.py
```

## 🎮 Uso del Sistema

### Acceso a la Aplicación

1. **Chat Público**: `http://localhost:8501`
   - Interfaz principal para consultas de clientes
   - Respuestas automáticas basadas en documentos

2. **Panel de Administración**: `http://localhost:8501/admin`
   - Usuario: `admin`
   - Contraseña: `admin123`
   - Gestión de documentos y configuración

### Ejemplos de Consultas

- "¿Cuál es la política de devoluciones de EcoMarket?"
- "¿Qué productos no aplican para devoluciones?"
- "¿Tienen disponibilidad del Cargador Solar Portátil?"
- "¿Cuál es el precio del Cargador Solar Portátil?"
- "¿Cuál es el teléfono para devoluciones?"
- "¿Cuál es el WhatsApp de soporte?"

## 🔧 Configuración Avanzada

### Personalizar el Sistema

1. **Agregar Documentos**: Coloca archivos en `static/sample_documents/`
2. **Modificar Prompts**: Edita `utils/vector_functions.py`
3. **Cambiar Temas**: Modifica `config/theme_config.py`
4. **Ajustar Chunking**: Configura `create_optimal_splitter()`

### Variables de Entorno Disponibles

```env
OPENAI_API_KEY=tu_api_key_openai
DOCKER_CONTAINER=true
DB_PATH=doc_sage.sqlite
PERSIST_DIRECTORY=./static/persist
```

## 🧪 Pruebas y Debugging

### Habilitar Logging Detallado

```python
# En views/public_chat.py
response = generate_answer_from_context(retriever, prompt, enable_logging=True)
```

### Verificar Estado del Sistema

```bash
# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs -f

# Verificar base de datos
sqlite3 doc_sage.sqlite ".tables"
```

## 📊 Características Técnicas

### Optimizaciones Implementadas

- **Chunking Adaptativo**: Ajusta parámetros según tipo de contenido
- **Prompts Especializados**: Evita alucinaciones del LLM
- **Configuración de Base de Datos**: WAL mode para mejor concurrencia
- **Manejo de Errores**: Reintentos automáticos y logging detallado
- **Detección Inteligente**: Identifica consultas de contacto automáticamente

### Configuración del LLM

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,  # Respuestas más precisas
    max_tokens=500,   # Respuestas concisas
)
```

## 🛠️ Estructura del Proyecto

```
GENERATIVE_AI_ICESI/
├── 📁 app.py                    # Aplicación principal Streamlit
├── 📁 init_app.py              # Script de inicialización
├── 📁 requirements.txt         # Dependencias Python
├── 📁 docker-compose.yml       # Configuración Docker
├── 📁 Dockerfile              # Imagen Docker
├── 📁 nginx.conf              # Configuración Nginx
│
├── 📁 config/                 # Configuración
│   └── theme_config.py        # Temas de la interfaz
│
├── 📁 controllers/            # Controladores
│   └── auth.py               # Autenticación
│
├── 📁 models/                 # Modelos de datos
│   └── db.py                 # Base de datos SQLite
│
├── 📁 utils/                  # Utilidades
│   ├── vector_functions.py   # Funciones RAG
│   └── theme_utils.py        # Utilidades de tema
│
├── 📁 views/                  # Vistas
│   ├── public_chat.py        # Chat público
│   ├── admin_login.py        # Login admin
│   └── admin_panel.py        # Panel admin
│
├── 📁 static/                 # Archivos estáticos
│   ├── 📁 sample_documents/  # Documentos de muestra
│   └── 📁 persist/           # Base de datos vectorial
│
└── 📁 fase1 y fase 2/        # Documentación
    └── ECOMARKET.md          # Documentación técnica
```

## 🚨 Solución de Problemas

### Error: "database is locked"
```bash
# Reiniciar la aplicación
docker-compose restart
```

### Error: "OPENAI_API_KEY not found"
```bash
# Verificar variables de entorno
echo $OPENAI_API_KEY
# O en Docker
docker-compose exec app env | grep OPENAI
```

### Documentos no se cargan
```bash
# Verificar permisos de archivos
ls -la static/sample_documents/
# Reinicializar colección
docker-compose exec app python init_app.py
```

## 📈 Consideraciones Éticas

- Se prioriza la transparencia en las fuentes utilizadas
- El sistema no reemplaza la supervisión humana
- Se evita la generación de respuestas fuera del contexto documental
- Implementa prompts estrictos para evitar alucinaciones
- Logging detallado para auditoría y debugging

## 📞 Soporte

Para problemas técnicos o consultas sobre el sistema, contacta al equipo de desarrollo o revisa los logs de la aplicación.