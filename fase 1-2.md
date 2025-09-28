## Universidad Icesi GenAI - Taller práctico #1 

## Claudia Martínez, Enrique Manzano, Mario J Castellanos

# Caso de Estudio: Optimización de la Atención al Cliente en una Empresa de E-commerce

## Fase 1: Selección y Justificación del Modelo de IA

### Tipo de Modelo

Hemos seleccionado un enfoque híbrido que combina RAG con un modelo
conversacional en la nube. Esto significa usar un modelo generativo en
la nube (por ejemplo, los de OpenAI, Anthropic o Gemini) para dar
respuestas automáticas y en múltiples turnos, complementado con
Retrieval-Augmented Generation (RAG), que aprovecha una base de
conocimiento y búsquedas vectoriales. Además, se establecen reglas de
enrutamiento hacia agentes humanos para atender el 20% de los casos más
complejos. Con esta estrategia se logra equilibrar velocidad, calidad y
costos operativos.

Probamos distintos modelos de Hugging Face, entre ellos
**google/flan-t5-base** y **tiiuae/falcon-7b-instruct**; sin embargo, en
ambos casos las respuestas a las consultas de los clientes resultaron
incorrectas. También intentamos utilizar
**mistralai/Mistral-7B-Instruct-v0.2**, pero no logramos acceder a él
debido a restricciones de permisos.

Finalmente, optamos por emplear el modelo **gemini-flash-latest**, que
utilizamos para implementar las dos soluciones propuestas.

## Arquitectura

![](./Imagen%201.png){size="2" width="300"}

## Arquitectura para el 80% de las consultas que son repetitivas (estado del pedido, devoluciones, características del producto)

1.  **Fuente de datos estructurados**

    -   Una **base de datos simulada de pedidos (self.pedidos_db)** con
        información clave: cliente, estado, carrier y fecha estimada.

    -   Permite respuestas factuales para consultas con número de
        pedido.

2.  **Fuente de datos no estructurados**

    -   Un conjunto de **documentos adicionales (self.documentos)** que
        contienen políticas, FAQs y descripciones de procesos.

    -   Se convierten en embeddings semánticos con
        **sentence-transformers/all-MiniLM-L6-v2**.

3.  **Módulo de recuperación (RAG)**

    -   Ante una consulta, se generan embeddings de la pregunta y se
        calculan similitudes con los documentos.

    -   Se seleccionan los más relevantes como **contexto** para
        enriquecer la respuesta.

4.  **Modelo generativo en la nube**

    -   **Gemini Flash Latest (gemini-flash-latest)** se encarga de
        **redactar la respuesta final** en español, empática y concisa.

    -   El prompt incluye:

        -   Datos del pedido (si aplica).

        -   Contexto recuperado por RAG.

        -   Mensaje original del cliente.

5.  **Gestión de estado de la conversación**

    -   El asistente guarda el último número de pedido mencionado para
        dar continuidad en consultas subsecuentes.

6.  **Control de errores y fallback**

    -   Si no se encuentra un pedido o no hay clave de API, el sistema
        responde con mensajes claros de error.

Arquitectura para abordar el **20% de consultas más complejas de
atención al cliente en EcoMarket** (quejas, problemas técnicos,
sugerencias).

### 1. **Instalación y configuración**

-   Instalación de la librería google-generativeai.

-   Configuración de la API Key de Gemini (idealmente con *Colab
    Secrets*).

-   Inicialización del modelo **gemini-flash-latest**.

### 2. **Definición del asistente empático**

Clase EcoMarketEmpatheticAssistant, con tres bloques principales:

#### a) **Diccionarios de soporte**

-   **Validaciones emocionales**: frases empáticas adaptadas a emociones
    detectadas (molesto, enojado, frustrado, preocupado, decepcionado,
    confundido, neutral).

-   **Tipos de problemas**: categorías de incidentes (producto_dañado,
    entrega_tardia, producto_incorrecto, servicio_cliente, facturacion,
    otro) con:

    -   Acciones sugeridas.

    -   Opciones de solución.

    -   Tiempo de respuesta esperado.

#### b) **Gestión de tickets**

-   Generación incremental de tickets únicos (T-1000, T-1001, etc.).

#### c) **Módulos principales**

1.  **analizar_mensajes_batch**

    -   Envía múltiples mensajes de clientes en una sola llamada a
        Gemini.

    -   Clasifica cada mensaje en **emoción** y **tipo de problema**.

    -   Maneja la respuesta en formato JSON y aplica *fallbacks* si el
        modelo falla.

    -   Garantiza correspondencia entre cada mensaje y su clasificación.

2.  **generar_respuesta_empatica**

    -   Combina la emoción y el tipo de problema detectados.

    -   Elige una validación emocional adecuada.

    -   Sugiere acciones y opciones de solución.

    -   Crea un ticket de seguimiento con tiempo de respuesta estimado.

    -   Devuelve una respuesta completa, empática y personalizada.

### 3. **Pruebas**

-   Se define una lista de mensajes de prueba (quejas por producto
    dañado, retraso en entrega, error de facturación, etc.).

-   Se procesan en *batch* con Gemini para clasificar emoción +
    problema.

-   Se genera y muestra la respuesta empática para cada caso.

A nivel de arquitectura, el flujo es:

Entrada del cliente (mensaje complejo)

↓

Clasificación batch con Gemini (emoción + problema)

↓

Selección de validaciones emocionales y acciones de soporte

↓

Construcción de respuesta empática personalizada

↓

Generación de ticket y entrega al cliente

## 

Este sistema aplica un **patrón clásico de RAG para atención al
cliente**, que se puede describir así:

Entrada del cliente → Extracción de intención y datos (regex)

→ Recuperación de contexto relevante (embeddings + búsqueda semántica)

→ Construcción de prompt (pedido + contexto + consulta)

→ Generación de respuesta (Gemini Flash Latest)

→ Entrega al cliente

En otras palabras: es una **arquitectura híbrida de generación aumentada
con recuperación (RAG)**, donde **Gemini actúa como cerebro generador**
y el **módulo de embeddings como memoria de conocimiento**.

A continuación hemos descrito lo que entendemos de cada uno de los
criterios para explicar los modelos que escogimos:

1\. Coste: Los modelos open-source autoalojados resultan más económicos
a largo plazo, seguidos de las opciones en la nube para grandes
volúmenes. Para picos de demanda, la nube ofrece flexibilidad, aunque
con un costo medio.

2\. Escalabilidad: Los modelos en la nube son los más escalables, luego
los autoalojados (si se cuenta con una infraestructura robusta), y
finalmente los modelos ligeros para triage.

3\. Facilidad de integración: La nube gana por su sencillez (APIs, SDKs
listos), seguida por los modelos ligeros; los modelos autoalojados
requieren bastante más trabajo técnico.

4\. Calidad de respuestas: Los modelos en la nube se destacan sin
dificultad, mientras que los open-source pueden igualarlos con buen
fine-tuning. Los modelos ligeros quedan en último lugar. En la tabla 1
describimos elementos favorables y desfavorables que justifican el
modelo híbrido seleccionado conforme a los criterios.

5\. Ideal para que: La nube aporta alta calidad y estructura, mientras
que los modelos autoalojados son perfectos para las empresas que desean
tener control de sus datos y pueden costear su infraestructura.

Tabla 1 - Caracterización de los modelos

| Modelo | Modelos en la nube gestionados (ej. OpenAI, Anthropic) | Modelos open-source autoalojados (ej. Llama, Mistral, Falcon) | Modelos ligeros para triage (ej. modelos pequeños optimizados) |
|----|----|----|----|
| Costo | Medio–alto por consulta, pero se paga solo por uso, lo que permite pruebas rápidas y pasar a producción fácilmente. | Requieren una mayor inversión inicial en infraestructura, pero el coste marginal después es mucho menor. | Muy bajo por consulta, se usan para clasificar y dirigir mensajes (por ejemplo, distinguir entre FAQ y casos que requieren humanos). |
| Escalabilidad | Excelente, con autoscaling y acuerdos de nivel de servicio (SLAs). | Depende de la infraestructura; se necesitan equipos DevOps y GPUs para escalar. | Muy sencilla, casi trivial. |
| Integración | Muy sencilla gracias a APIs, webhooks y SDKs | Flexible, pero conlleva más esfuerzo de ingeniería. | Muy sencilla, casi trivial. |
| Calidad. | Muy alta, se destacan en manejo de tono, empatía y seguridad, especialmente con fine-tuning o prompts de sistema. | Muy buena si se ajustan con fine-tuning/ instrucciones, varía según la versión usada. | Suficiente para clasificación de intenciones, pero no adecuados para respuestas complejas con empatía. |
| Ideal para | Lanzamientos rápidos que requieren alta calidad. | Organizaciones que priorizan control de datos, ahorro a largo plazo y cumplimiento normativo estricto. |  |

## Fase 2: Evaluación de Fortalezas, Limitaciones y Riesgos Éticos

### Fortalezas

1\. Eficiencia en costos: La IA puede gestionar grandes volúmenes de
mensajes con un gasto mínimo. Por ejemplo, manejar 100,000 consultas
cuesta alrededor de 40 dólares. 2. Escalabilidad inmediata: Es capaz de
responder en segundos a miles de interacciones, sin necesidad de ampliar
el equipo humano.

2\. Alta precisión en FAQs: Ofrece respuestas muy acertadas en temas
repetitivos como estado de pedidos, devoluciones o información de
productos.

3\. Empatía programable: Con el diseño adecuado de prompts, puede
mantener un tono cercano y coherente con los valores eco-friendly de la
empresa.

4\. Disponibilidad 24/7: Brinda atención continua en cualquier momento,
lo que mejora la experiencia y satisfacción del cliente.

### Limitaciones

1\. Alucinaciones: puede inventar detalles (ej. plazos de envío
incorrectos, políticas inexistentes).

2\. Sesgo: refleja patrones de los datos con que fue entrenado, lo que
puede producir respuestas culturalmente sesgadas o poco inclusivas. .
Privacidad: si no se controla, podría almacenar o exponer datos
sensibles de clientes (emails, direcciones, números de pedido).

3\. Dependencia tecnológica: requiere conexión estable y costos de API
(aunque bajos, pueden crecer si no se controla el uso).

4\. Limitaciones contextuales: no accede a información en tiempo real a
menos que se integre con sistemas internos (ERP, CRM, etc.).

### Riesgos éticos

Hemos elaborado la siguiente matriz de riesgos y mitigaciones,
considerando el tipo de empresa de atención al cliente, ver tabla 2.

Tabla 2 - Matriz de riesgo y mitigaciones.

  
| **Riesgo ético técnico** | **Descripción** | **Impacto** | **Probabilidad** | **Mitigación recomendada** |
|----|----|----|----|----|
| Alucinaciones | El modelo puede inventar políticas, plazos o características inexistentes. | Alto (afecta confianza del cliente). | Media | Integrar RAG (Retrieval-Augmented Generation) con base de datos oficial; monitoreo de calidad; alertas para respuestas dudosas. |
| Sesgo en respuestas. | Posibles diferencias de trato según idioma, género o contexto cultural. | Medio | Media | Auditoría periódica de sesgos; fine-tuning con datos inclusivos; guías de lenguaje neutral y empático. |
| Privacidad de datos | Riesgo de exponer información sensible (nombres, direcciones, correos). | Muy alto (riesgo legal y reputacional). | Alta | Anonimización antes de enviar a la IA; cumplimiento GDPR/CCPA; logs encriptados; acuerdos de procesamiento de datos con proveedores. |
| Impacto laboral | Reducción de tareas repetitivas para agentes humanos. | Medio (riesgo social y cultural). | Alta | Reentrenamiento de personal para casos complejos; creación de roles en supervisión de IA, análisis de feedback y experiencia de cliente. |
| Dependencia tecnológica | Fallos en el servicio del proveedor de IA pueden interrumpir soporte. | Medio | Media | Estrategia multicloud o fallback a FAQs automatizadas internas; monitoreo de SLA del proveedor. |
| Costo oculto por escalado | Uso excesivo de tokens puede incrementar la factura. | Bajo | Media | Optimizar prompts para reducir tokens; establecer límites y alertas de consumo. |


