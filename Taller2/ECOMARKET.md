**ECOMARKET**

**Documentación del Sistema RAG para Atención al Cliente – EcoMarket**

**Fase 1: Selección de Componentes del Sistema RAG**

**🔹 Modelo de Embeddings seleccionado:**   
Se utilizó nomic-embed-text, descargado e integrado mediante Ollama. Este modelo fue elegido por su capacidad para generar representaciones semánticas precisas en español, su disponibilidad gratuita y su compatibilidad con LangChain.

**🔹 Base de datos vectorial utilizada:**   
Se empleó **FAISS**, una solución eficiente y de código abierto para búsquedas por similitud. Se eligió por su facilidad de integración, buen rendimiento en entornos locales y bajo costo operativo, ideal para un prototipo funcional en Google Colab.

**Fase 2: Creación de la Base de Conocimiento**

**🔹 Documentos utilizados:**

| **Tipo de documento** | **Archivo**                  | **Contenido**                                       |
|-----------------------|------------------------------|-----------------------------------------------------|
| PDF                   | Política de Devoluciones.pdf | Normativa de reembolsos y condiciones de devolución |
| Excel                 | Inventario_Sostenible.xlsx   | Información de productos, stock y precios           |
| JSON                  | faq.json                     | Preguntas frecuentes de clientes                    |

**🔹 Estrategia de segmentación (chunking):**   
Se aplicó RecursiveCharacterTextSplitter con chunk_size=500 y chunk_overlap=50. Esta técnica permite conservar coherencia semántica en los fragmentos, facilitando la recuperación contextual por el sistema RAG.

**🔹 Indexación:**   
Los documentos fueron convertidos en vectores mediante el modelo de embeddings y almacenados en FAISS. Se generó una base local llamada faiss_ecoshop, que permite búsquedas rápidas y precisas.

**Fase 3: Integración y Ejecución del Código**

**🔹 Entorno de trabajo:**   
Google Colab, con instalación de dependencias específicas como langchain-community, faiss-cpu, pypdf, unstructured, msoffcrypto-tool y jq.

**🔹 Carga de documentos:**   
Se utilizaron loaders especializados para cada tipo de archivo (PDF, Excel, JSON). Los datos del Excel fueron transformados manualmente en objetos Document para conservar el contexto semántico.

**🔹 Construcción del pipeline RAG:**   
Se integró el modelo llama3.2:3b mediante Ollama como LLM principal. El sistema RetrievalQA se configuró con búsqueda por similitud (k=3) para recuperar los fragmentos más relevantes.

**🔹 Pruebas del sistema:**   
Se realizaron consultas típicas de atención al cliente, como disponibilidad de productos, precios, condiciones de devolución y contacto con soporte. El sistema respondió con precisión utilizando la base de conocimiento indexada.
