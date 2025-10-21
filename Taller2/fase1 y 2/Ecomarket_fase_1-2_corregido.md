Documentando el sistema RAG de atención al cliente para EcoMarket.

Integrantes: Claudia Martinez

Mario Castellanos

Enrique Manzano

# Sistema RAG para Atención al Cliente – EcoMarket

## Introducción

A continuación describimos la implementación de un sistema RAG para optimizar la atención al cliente de EcoMarket, plataforma de e-commerce especializada en productos sostenibles. El sistema permite al asistente virtual consultar una base de conocimiento interna antes de generar respuestas, eliminando alucinaciones y garantizando información precisa y actualizada.

## Fase 1: Selección de Componentes del Sistema RAG

### Modelo de Embeddings

Hemos seleccionado Nomic Embed Text integrado a través de Ollama dado que tiene características como soporte multilingüe optimizado, está específicamente entrenado para manejar múltiples idiomas, incluyendo el español, con representaciones semánticas de alta calidad. Esto es crucial para EcoMarket, cuya documentación y consultas de clientes se hacen en español. De igual manera Genera incrustaciones de 768 dimensiones, ofreciendo un balance óptimo entre precisión semántica y eficiencia computacional. Esto permite búsquedas rápidas sin sacrificar calidad, proporcionando dimensionalidad eficiente.

Como es un modelo de código abierto ejecutable localmente mediante Ollama, elimina costos recurrentes de APIs propietarias como OpenAI Embeddings (que costaría alrededor de \$0.13 por millón de tokens) o Cohere Embeddings. Se integra de forma nativa con la librería Langchain Community proporcionando soporte directo para Ollama, simplificando la implementación y reduciendo la complejidad del código. Como se ejecuta localmente, no se envían datos sensibles de clientes o documentos internos a servicios externos, cumpliendo con regulaciones de protección de datos.

Revisamos otras alternativas como los modelos de OpenAI text-embedding-3-small que son muy precisos pero costosos en su operación y dependen de servicios externos. Igualmente revisamos Sentence Transformers de Hugging Face que requiere configuración manual más compleja y mayor uso de memoria GPU, por eso seleccionamos este Nomic Embed Text.

### Base de Datos Vectorial

Para este componente seleccionamos FAISS (Facebook AI Similarity Search) dado que FAISS utiliza algoritmos optimizados (como HNSW y IVF) que permiten búsquedas extremadamente rápidas incluso con millones de vectores. Para el caso de EcoMarket con alrededor de 21 chunks, las búsquedas son prácticamente instantáneas (\<10ms). Adicionalmente tiene facilidad de implementación: ya que no requiere infraestructura adicional (servidores, bases de datos externas) ni configuración compleja. Se integra directamente en el código Python y permite persistencia local mediante el método save_local().

Esta librería tiene costo operativo cero por ser de código abierto y ejecutarse localmente, no genera costos de hosting o almacenamiento en la nube, ideal para prototipos y despliegues iniciales. Soporta escalabilidad horizontal, aunque inicialmente se ejecute localmente, porque soporta sharding y distribución en múltiples nodos para manejar millones de documentos si EcoMarket crece. Por último es compatible con LangChain, la cual ofrece una clase FAISS que abstrae completamente la complejidad de indexación y búsqueda, permitiendo código limpio y mantenible.

### Análisis comparativo de bases de datos vectoriales

| Característica | FAISS | Pinecone | ChromaDB | Weaviate |
|----|----|----|----|----|
| Costo | Gratuito | 70/mes (tier inicial) | Gratuito | Gratuito (self-hosted) |
| Despliegue | Local | Cloud | Local/Cloud | Local/Cloud |
| Escalabilidad | Alta (con configuración) | Muy alta (administrada) | Media | Alta |
| Latencia búsqueda | \< 10ms (local) | aprox.50-100ms (red) | aprox. 15ms (local) | aprox. 20ms (local) |
| Facilidad uso | Media | Alta | Alta | Media |
| Mejor para | Prototipos, bajo volumen | Producción, alto tráfico | Desarrollo rápido | Apps semánticas complejas. |

Para el caso de EcoMarket en fase inicial, FAISS es la opción óptima por su rendimiento local y cero costos. Si el sistema escala a \>100k consultas/día, la mejor opción sería migrar a Pinecone para aprovechar su infraestructura administrada.

## Fase 2: Creación de la Base de Conocimiento

### Documentos Identificados

| Tipo | Archivo | Contenido | Justificación |
|----|----|----|----|
| PDF | Política de Devoluciones.pdf | Condiciones de reembolso, plazos, excepciones, procedimientos | Las políticas de devolución son la consulta más frecuente en e-commerce. Formato PDF es estándar para documentos normativos. |
| Excel | Inventario_Sostenible.xlsx | Catálogo de productos: nombre, categoría, stock, precios, fechas de ingreso | Información dinámica que cambia frecuentemente. Excel permite actualizaciones rápidas por equipos no técnicos. |
| JSON | faq.json | Preguntas frecuentes estructuradas con pares pregunta-respuesta | Formato ideal para datos estructurados. Facilita expansión incremental de respuestas comunes. |

### Estrategia de Segmentación (Chunking)

Utilizamos el método RecursiveCharacterTextSplitter con 500 caracteres por fragmento (chunk_size) y 50 de solapamiento entre chunks consecutivos (chunk_overlap).

Para preservar la coherencia semántica, este método recursivo intenta dividir primero por separadores naturales (párrafos, oraciones, palabras) antes de cortar por caracteres arbitrarios. Esto evita fragmentar conceptos relacionados. El tamaño óptimo para retieval es de 500 caracteres (de 100 a 120 tokens), con este parámetro el chunk contiene suficiente texto para ser autocontenido y no es tan grande como para diluir la relevancia semántica. Permite recuperar 3-5 chunks sin exceder la ventana de contexto del LLM.

El solapamiento de 50 caracteres (10%) garantiza que información importante cerca de los límites del chunk no se pierda. Esto es crítico para mantener continuidad en listas, tablas o políticas multipunto. El sistema generó 21 chunks totales desde los 3 documentos, un número manejable que permite búsquedas rápidas y recuperación precisa.

### Proceso de Indexación

Pipeline implementado:

1.  Carga de documentos:

-   PDF: PyPDFLoader extrae texto preservando estructura de párrafos
-   JSON: JSONLoader con jq_schema='.' procesa cada par pregunta-respuesta como un documento independiente
-   Excel: Transformación manual en objetos Document con formato enriquecido:

 ```
  python content = f"Producto: {row['Nombre']}\\n"
                   f"Categoría: {row['Categoría']}\\n"
                   f"Stock: {row['Cantidad en Stock']}\\n"
                   f"Precio: {row['Precio']} dólares\\n"
```
2.  Segmentación:

-   Aplicación de RecursiveCharacterTextSplitter sobre los documentos combinados
-   Resultado: 21 chunks con metadatos preservados (archivo fuente)

4.  Vectorización:

-   Cada chunk se convierte en un embedding de 768 dimensiones mediante nomic-embed-text
-   Proceso toma proximadamete 1.5 segundos para los 21 chunks

5.  Almacenamiento:

-   Los vectores se indexan en FAISS con algoritmo Flat (fuerza bruta) dado el bajo volumen
-   Base guardada localmente en faiss_ecoshop/ para persistencia entre sesiones.

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

EcoMarket-RAG/

│

├── data/ \# Documentos fuente (PDF, Excel, JSON)

├── notebook/ \# Notebook con el código completo

├── outputs/ \# Resultados de pruebas (opcional)

├── README.md \# Documentación del proyecto

└── faiss_ecoshop/ \# Base vectorial local (FAISS)

# Fase 3: Integración y Ejecución del Código

### Entorno de trabajo:   
Google Colab, con instalación de dependencias específicas como langchain-community, faiss-cpu, pypdf, unstructured, msoffcrypto-tool y jq.

### Carga de documentos:   
Se utilizaron loaders especializados para cada tipo de archivo (PDF, Excel, JSON). Los datos del Excel fueron transformados manualmente en objetos Document para conservar el contexto semántico.

### Construcción del pipeline RAG:   
Se integró el modelo llama3.2:3b mediante Ollama como LLM principal. El sistema RetrievalQA se configuró con búsqueda por similitud (k=3) para recuperar los fragmentos más relevantes.

### Pruebas del sistema:   
Se realizaron consultas típicas de atención al cliente, como disponibilidad de productos, precios, condiciones de devolución y contacto con soporte. El sistema respondió con precisión utilizando la base de conocimiento indexada.
