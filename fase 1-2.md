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

  ------------------------------------------------------------------------
  Modelo            Modelos en la     Modelos            Modelos ligeros
                    nube gestionados  open-source        para triage (ej.
                    (ej. OpenAI,      autoalojados (ej.  modelos pequeños
                    Anthropic)        Llama, Mistral,    optimizados)
                                      Falcon)            
  ----------------- ----------------- ------------------ -----------------
  \-\-\--           \-\-\--           \-\-\--            \-\-\--

  Costo             Medio--alto por   Requieren una      Muy bajo por
                    consulta, pero se mayor inversión    consulta, se usan
                    paga solo por     inicial en         para clasificar y
                    uso, lo que       infraestructura,   dirigir mensajes
                    permite pruebas   pero el coste      (por ejemplo,
                    rápidas y pasar a marginal después   distinguir entre
                    producción        es mucho menor.    FAQ y casos que
                    fácilmente.                          requieren
                                                         humanos).

  Escalabilidad     Excelente, con    Depende de la      Muy sencilla,
                    autoscaling y     infraestructura;   casi trivial.
                    acuerdos de nivel se necesitan       
                    de servicio       equipos DevOps y   
                    (SLAs).           GPUs para escalar. 

  Integración       Muy sencilla      Flexible, pero     Muy sencilla,
                    gracias a APIs,   conlleva más       casi trivial.
                    webhooks y SDKs   esfuerzo de        
                                      ingeniería.        

  Calidad.          Muy alta, se      Muy buena si se    Suficiente para
                    destacan en       ajustan con        clasificación de
                    manejo de tono,   fine-tuning/       intenciones, pero
                    empatía y         instrucciones,     no adecuados para
                    seguridad,        varía según la     respuestas
                    especialmente con versión usada.     complejas con
                    fine-tuning o                        empatía.
                    prompts de                           
                    sistema.                             

  Ideal para        Lanzamientos      Organizaciones que 
                    rápidos que       priorizan control  
                    requieren alta    de datos, ahorro a 
                    calidad.          largo plazo y      
                                      cumplimiento       
                                      normativo          
                                      estricto.          
  ------------------------------------------------------------------------

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

  -----------------------------------------------------------------------------------------------------
  \*\*Riesgo      \*\*Descripción\*\*   \*\*Impacto\*\*   \*\*Probabilidad\*\*   \*\*Mitigación
  ético                                                                          recomendada\*\*
  técnico\*\*                                                                    
  --------------- --------------------- ----------------- ---------------------- ----------------------
  \-\-\--         \-\-\--               \-\-\--           \-\-\--                \-\-\--

  Alucinaciones   El modelo puede       Alto (afecta      Media                  Integrar RAG
                  inventar políticas,   confianza del                            (Retrieval-Augmented
                  plazos o              cliente).                                Generation) con base
                  características                                                de datos oficial;
                  inexistentes.                                                  monitoreo de calidad;
                                                                                 alertas para
                                                                                 respuestas dudosas.

  Sesgo en        Posibles diferencias  Medio             Media                  Auditoría periódica de
  respuestas.     de trato según                                                 sesgos; fine-tuning
                  idioma, género o                                               con datos inclusivos;
                  contexto cultural.                                             guías de lenguaje
                                                                                 neutral y empático.

  Privacidad de   Riesgo de exponer     Muy alto (riesgo  Alta                   Anonimización antes de
  datos           información sensible  legal y                                  enviar a la IA;
                  (nombres,             reputacional).                           cumplimiento
                  direcciones,                                                   GDPR/CCPA; logs
                  correos).                                                      encriptados; acuerdos
                                                                                 de procesamiento de
                                                                                 datos con proveedores.

  Impacto laboral Reducción de tareas   Medio (riesgo     Alta                   Reentrenamiento de
                  repetitivas para      social y                                 personal para casos
                  agentes humanos.      cultural).                               complejos; creación de
                                                                                 roles en supervisión
                                                                                 de IA, análisis de
                                                                                 feedback y experiencia
                                                                                 de cliente.

  Dependencia     Fallos en el servicio Medio             Media                  Estrategia multicloud
  tecnológica     del proveedor de IA                                            o fallback a FAQs
                  pueden interrumpir                                             automatizadas
                  soporte.                                                       internas; monitoreo de
                                                                                 SLA del proveedor.

  Costo oculto    Uso excesivo de       Bajo              Media                  Optimizar prompts para
  por escalado    tokens puede                                                   reducir tokens;
                  incrementar la                                                 establecer límites y
                  factura.                                                       alertas de consumo.
  -----------------------------------------------------------------------------------------------------
