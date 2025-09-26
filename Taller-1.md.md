---
title: "T1"
output: 
  html_document: 
    keep_md: true
date: "2025-09-22"
---



## Universidad Icesi GenAI - Taller práctico #1 2025.09.21 Claudia Martínez, Enrique Manzano, Mario J Castellanos

# Caso de Estudio: Optimización de la Atención al Cliente en una Empresa de E-commerce

## Fase 1: Selección y Justificación del Modelo de IA

### Tipo de Modelo

Hemos seleccionado un enfoque híbrido que combina RAG con un modelo conversacional en la nube. Esto significa usar un modelo generativo en la nube (por ejemplo, los de OpenAI o Anthropic) para dar respuestas automáticas y en múltiples turnos, complementado con Retrieval-Augmented Generation (RAG), que aprovecha una base de conocimiento y búsquedas vectoriales. Además, se establecen reglas de enrutamiento hacia agentes humanos para atender el 20% de los casos más complejos. Con esta estrategia se logra equilibrar velocidad, calidad y costos operativos.

## Arquitectura

![](images/Imagen%201.png){size="2" style="text-align: right" width="300"}

Figura 1. Arquitectura del enfoque híbrido propuesto

En la arquitectura que proponemos, ver figura 1, se centralizan todos los canales de ingreso como chat, correo, redes sociales, en una capa que estandariza los mensajes. Seguidamente un modelo ligero de triage clasifica cada interacción en categorías como FAQ, devoluciones, quejas o temas técnicos.

Para las respuestas automáticas a consultas repetitivas, proponemos el uso de una base de datos vectorial (Milvus, Pinecone, Weaviate) con FAQs, historial de pedidos y políticas y un modelo conversacional en la nube que genera la respuesta basándose en la información recuperada. Para las respuestas más complicadas que necesitan de interacción humana se configuran reglas y un “modo asistido” que permitan que el agente vea y edite la sugerencia de la IA antes de enviarla.

Por último se implementaría un registro de interacciones, métricas de satisfacción, tasa de reescalado y filtros para contenido sensible más un bucle de retroalimentación para reentrenar o ajustar el modelo con casos reales como ciclo de mejora continua.

A continuación hemos descrito lo que entendemos de cada uno de los criterios para explicar los modelos que escogimos:

1.  Coste: Los modelos open-source autoalojados resultan más económicos a largo plazo, seguidos de las opciones en la nube para grandes volúmenes. Para picos de demanda, la nube ofrece flexibilidad, aunque con un costo medio.
2.  Escalabilidad: Los modelos en la nube son los más escalables, luego los autoalojados (si se cuenta con una infraestructura robusta), y finalmente los modelos ligeros para triage.
3.  Facilidad de integración: La nube gana por su sencillez (APIs, SDKs listos), seguida por los modelos ligeros; los modelos autoalojados requieren bastante más trabajo técnico.
4.  Calidad de respuestas: Los modelos en la nube se destacan sin dificultad, mientras que los open-source pueden igualarlos con buen fine-tuning. Los modelos ligeros quedan en último lugar. En la tabla 1 describimos elementos favorables y desfavorables que justifican el modelo híbrido seleccionado conforme a los criterios.
5.  Ideal para que: La nube aporta alta calidad y estructura, mientras que los modelos autoalojados son perfectos para las empresas que desean tener control de sus datos y pueden costear su infraestructura.

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

1.  Eficiencia en costos: La IA puede gestionar grandes volúmenes de mensajes con un gasto mínimo. Por ejemplo, manejar 100,000 consultas cuesta alrededor de 40 dólares. 2. Escalabilidad inmediata: Es capaz de responder en segundos a miles de interacciones, sin necesidad de ampliar el equipo humano.
2.  Alta precisión en FAQs: Ofrece respuestas muy acertadas en temas repetitivos como estado de pedidos, devoluciones o información de productos.
3.  Empatía programable: Con el diseño adecuado de prompts, puede mantener un tono cercano y coherente con los valores eco-friendly de la empresa.
4.  Disponibilidad 24/7: Brinda atención continua en cualquier momento, lo que mejora la experiencia y satisfacción del cliente.

### Limitaciones

1.  Alucinaciones: puede inventar detalles (ej. plazos de envío incorrectos, políticas inexistentes).
2.  Sesgo: refleja patrones de los datos con que fue entrenado, lo que puede producir respuestas culturalmente sesgadas o poco inclusivas. . Privacidad: si no se controla, podría almacenar o exponer datos sensibles de clientes (emails, direcciones, números de pedido).
3.  Dependencia tecnológica: requiere conexión estable y costos de API (aunque bajos, pueden crecer si no se controla el uso).
4.  Limitaciones contextuales: no accede a información en tiempo real a menos que se integre con sistemas internos (ERP, CRM, etc.).

### Riesgos éticos

Hemos elaborado la siguiente matriz de riesgos y mitigaciones, considerando el tipo de empresa de atención al cliente, ver tabla 2.

Tabla 2 - Matriz de riesgo y mitigaciones.

| **Riesgo ético técnico** | **Descripción** | **Impacto** | **Probabilidad** | **Mitigación recomendada** |
|----|----|----|----|----|
| Alucinaciones | El modelo puede inventar políticas, plazos o características inexistentes. | Alto (afecta confianza del cliente). | Media | Integrar RAG (Retrieval-Augmented Generation) con base de datos oficial; monitoreo de calidad; alertas para respuestas dudosas. |
| Sesgo en respuestas. | Posibles diferencias de trato según idioma, género o contexto cultural. | Medio | Media | Auditoría periódica de sesgos; fine-tuning con datos inclusivos; guías de lenguaje neutral y empático. |
| Privacidad de datos | Riesgo de exponer información sensible (nombres, direcciones, correos). | Muy alto (riesgo legal y reputacional). | Alta | Anonimización antes de enviar a la IA; cumplimiento GDPR/CCPA; logs encriptados; acuerdos de procesamiento de datos con proveedores. |
| Impacto laboral | Reducción de tareas repetitivas para agentes humanos. | Medio (riesgo social y cultural). | Alta | Reentrenamiento de personal para casos complejos; creación de roles en supervisión de IA, análisis de feedback y experiencia de cliente. |
| Dependencia tecnológica | Fallos en el servicio del proveedor de IA pueden interrumpir soporte. | Medio | Media | Estrategia multicloud o fallback a FAQs automatizadas internas; monitoreo de SLA del proveedor. |
| Costo oculto por escalado | Uso excesivo de tokens puede incrementar la factura. | Bajo | Media | Optimizar prompts para reducir tokens; establecer límites y alertas de consumo. |

## Fase 3: Aplicación de la Ingeniería de Prompts

### Caso 1: Prompt de Solicitud de Pedido

Prompt para LLM pequeño (respuestas repetitivas, factual)

Eres un asistente de EcoMarket. Tu tarea es dar respuestas breves, claras y verificables sobre pedidos y productos. Nunca inventes información, usa solo lo que se te proporciona.

Datos del cliente:

-   Nombre: {{nombre}}

-   Pedido: {{id_pedido}} → Estado: {{estado}}, Carrier: {{carrier}}, ETA: {{fecha}}

Responde con tono amable y profesional:

Ejemplo:

Cliente: ¿Dónde está mi pedido #12345?

Respuesta: Hola {{nombre}}, tu pedido #12345 está {{estado}} con {{carrier}}. La fecha estimada de entrega es {{fecha}}. ¿Quieres el enlace de seguimiento?

### Caso 2: Prompt de Devolución de Producto:

Prompt para LLM grande (casos complejos/empatía)

Eres un asistente empático de EcoMarket. Tu tarea es atender quejas y consultas complejas. Muestra comprensión y ofrece soluciones claras. Mantén un tono humano, cálido y profesional.

Instrucciones:

-   Primero valida la emoción del cliente.
-   Luego explica la acción inmediata que tomarás.
-   Da opciones concretas (reembolso, reemplazo, ticket).
-   Si no tienes certeza, admite la limitación y ofrece contacto humano.

Ejemplo:

Cliente: “Estoy muy molesto, mi pedido llegó dañado.”

Respuesta: Lamento mucho que tu producto haya llegado en mal estado, entiendo tu frustración. Voy a abrir un caso prioritario ahora mismo. Para acelerar el proceso, ¿podrías compartir una foto del producto dañado? Puedes elegir entre reembolso o reemplazo inmediato. He creado el ticket T-789 y un agente te contactará en menos de 4 horas.

Prompt Clasificador de Intents

Clasifica la siguiente consulta del cliente en una de estas categorías:

-   estado_pedido
-   devolucion
-   caracteristicas_producto
-   queja
-   problema_tecnico
-   sugerencia

Devuelve solo la categoría, sin explicación.

Texto: "{{mensaje_cliente}}"
