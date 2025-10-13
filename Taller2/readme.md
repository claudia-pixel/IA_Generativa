Documentando el sistema RAG de atención al cliente para EcoMarket.


Integrantes: Claudia Martinez

Mario Castellanos

Enrique Manzano


**Sistema RAG para Atención al Cliente – EcoMarket**

Este proyecto implementa un sistema de generación aumentada por recuperación (RAG) para mejorar la atención al cliente de EcoMarket, una empresa de e-commerce sostenible. El sistema permite responder preguntas frecuentes y consultas sobre productos utilizando documentos internos como fuente confiable.

**Objetivos del Proyecto**

-   Integrar un modelo de lenguaje con recuperación semántica para responder consultas reales de clientes.
-   Utilizar documentos internos (PDF, Excel, JSON) como base de conocimiento.
-   Evaluar la precisión, transparencia y ética del sistema en un entorno educativo.

**Componentes del Sistema**

| **Componente** | **Herramienta elegida**     | **Justificación**                                         |
|----------------|-----------------------------|-----------------------------------------------------------|
| Embeddings     | nomic-embed-text vía Ollama | Precisión en español, gratuito, compatible con LangChain  |
| Vector DB      | FAISS                       | Código abierto, eficiente en local, ideal para prototipos |
| LLM            | llama3.2:3b vía Ollama      | Ligero, rápido y adecuado para tareas de QA               |
| Framework      | LangChain                   | Modular, flexible y orientado a sistemas RAG              |

**Documentos Utilizados**

-   **Política de Devoluciones** (PDF): Normativa oficial de reembolsos.
-   **Inventario Sostenible** (Excel): Productos, stock y precios.
-   **Preguntas Frecuentes** (JSON): Interacciones comunes con clientes.

Todos los documentos fueron segmentados en chunks de 500 caracteres con solapamiento de 50, usando RecursiveCharacterTextSplitter.

**Flujo del Sistema**

1.  **Carga de documentos** con loaders especializados.
2.  **Segmentación y vectorización** con embeddings Ollama.
3.  **Indexación en FAISS** y almacenamiento local.
4.  **Construcción del pipeline RAG** con RetrievalQA.
5.  **Pruebas de consulta** simulando preguntas reales de clientes.

**Ejemplos de Preguntas Respondidas**

-   ¿Cuál es la política de devoluciones de EcoMarket?
-   ¿Qué productos no aplican para devoluciones?
-   ¿Tienen disponibilidad del producto “Botella Reutilizable de Acero Inoxidable”?
-   ¿Cuál es el precio actual del Cargador Solar Portátil?

**Consideraciones Éticas**

-   Se priorizó la transparencia en las fuentes utilizadas.
-   El sistema no reemplaza la supervisión humana: se recomienda validación experta en casos sensibles.
-   Se evita la generación de respuestas fuera del contexto documental indexado.

**Estructura del Repositorio**

## Estructura del Repositorio
```
EcoMarket-RAG/
│
├── README.md
│    Documentación general del proyecto
│   (propósito, instalación, ejecución y resultados)
│
├── data/
│    Documentos fuente utilizados para construir la base de conocimiento del sistema RAG
│   │
│   ├── Política de Devoluciones.pdf
│   ├── Inventario_Sostenible.xlsx
│   ├── faq.json
│   │   → Preguntas frecuentes con respuestas
│   ├── faq_extra.json
│   │   → Preguntas inferenciales sin respuestas (para pruebas de razonamiento)
│   └── faq_devoluciones.json
│       → Preguntas específicas sobre políticas de devolución
│
├── notebooks/
│    Notebooks de desarrollo y pruebas
│   │
│   └── sistema_rag_ecomarket.ipynb
│       → Notebook principal con el flujo completo
│       (carga, embeddings, RAG y pruebas)
│
├── faiss_ecoshop/
│    Base vectorial FAISS generada localmente
│   │
│   └── index.faiss
│
├── evaluacion/
│    Recursos para validar el desempeño del sistema
│   │
│   ├── preguntas_prueba.json
│   │   → Set completo de preguntas de evaluación
│   ├── respuestas_esperadas.json
│   │   → (Opcional) Respuestas esperadas para evaluación automatizada
│   └── rubrica_evaluacion.md
│       → Criterios pedagógicos y éticos de evaluación
│
├── docs/
│    Documentación técnica y pedagógica complementaria
│   │
│   ├── arquitectura_rag.md
│   │   → Descripción y justificación de los componentes del sistema
│   ├── estrategia_chunking.md
│   │   → Análisis de segmentación de texto y su impacto
│   ├── indexacion_vectorial.md
│   │   → Explicación del proceso de embeddings y FAISS
│   └── limitaciones_supuestos.md
│       → Reflexión crítica sobre las limitaciones del sistema
│
├── config/
│   🔧 Archivos de configuración y conexión remota
│   │
│   └── ollama_ngrok_config.md
│       → Guía para exponer Ollama local vía ngrok


    
```



