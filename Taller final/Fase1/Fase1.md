# Proyecto Final: Implementación de un Agente de IA para Automatización de Tareas en EcoMarket

## Introducción

Desarrollamos este proyecto como la culminación de nuestro aprendizaje en la implementación de sistemas inteligentes basados en inteligencia artificial. Nuestro objetivo principal fue transformar el asistente de atención al cliente de EcoMarket en una herramienta proactiva capaz de automatizar procesos complejos, específicamente el manejo integral de devoluciones de productos. La solución que implementamos combina arquitecturas RAG (Retrieval-Augmented Generation) con agentes autónomos, permitiendo no solo responder consultas sino ejecutar acciones concretas de manera inteligente.

Integramos en nuestro sistema múltiples fuentes de información corporativa, incluyendo catálogos de productos, registros de pedidos, solicitudes de devolución y documentación de políticas. A través de técnicas avanzadas de procesamiento de lenguaje natural y aprendizaje automático, el agente que construimos puede comprender intenciones complejas, verificar elegibilidad para devoluciones, calcular reembolsos y registrar solicitudes de manera autónoma, todo mientras mantiene una comunicación natural y efectiva con los usuarios.

## Fase 1: Diseño de la Arquitectura del Agente

### Introducción al Diseño

Fundamentamos nuestra arquitectura del agente de IA en la necesidad de crear un sistema híbrido que combine capacidades de recuperación de información con ejecución de acciones concretas. El diseño que propusimos no solo busca responder preguntas sobre productos y políticas, sino también automatizar flujos de trabajo operativos relacionados con el proceso de devoluciones. Esta fase establece los cimientos conceptuales y técnicos sobre los cuales construimos toda la solución.

### Definición de las Herramientas (Tools)

Diseñamos un conjunto específico de herramientas que permiten al agente interactuar con los sistemas de EcoMarket de manera estructurada. Cada herramienta la concebimos siguiendo principios de responsabilidad única y comparabilidad, asegurando que el sistema sea mantenible y extensible. Las tres herramientas que implementamos constituyen el núcleo funcional del sistema de automatización.

#### Verificación de Elegibilidad de Producto

Concebimos esta herramienta como el primer punto de control en el proceso de devolución. Su función principal es determinar si un producto específico cumple con los criterios establecidos en las políticas de devolución de EcoMarket. La herramienta recibe información estructurada sobre el pedido, el producto, la fecha de compra y el motivo de la devolución.

La lógica de elegibilidad que implementamos se basa en criterios predefinidos que consideran aspectos como el estado del producto, clasificando motivos como defectuoso, dañado o no corresponde con el pedido. Evaluamos estos parámetros contra las políticas corporativas y retornamos una respuesta clara sobre la elegibilidad, incluyendo la justificación correspondiente. Diseñamos el formato de entrada para que sea intuitivo pero estructurado, utilizando punto y coma como separador entre los diferentes campos requeridos.

Cuando un cliente solicita una devolución, nuestra herramienta analiza primero el motivo proporcionado contra una lista de motivos válidos predefinidos. Si el motivo corresponde a un defecto del producto, daño durante el envío, o un error en el pedido, el sistema aprueba automáticamente la elegibilidad. En caso contrario, proporciona una explicación clara sobre por qué la solicitud no cumple con los criterios, manteniendo siempre un tono profesional y orientado al servicio al cliente.

#### Cálculo de Monto de Reembolso

Una vez confirmada la elegibilidad, desarrollamos esta herramienta para calcular el monto exacto que debe reembolsarse al cliente. La implementación considera no solo el precio unitario del producto sino también la cantidad de unidades devueltas, aplicando las reglas de negocio establecidas por EcoMarket.

Diseñamos el cálculo para tomar en cuenta factores como el precio base del producto y la cantidad de unidades afectadas. Nuestra herramienta asegura precisión en los cálculos y formatea la respuesta de manera clara para el usuario, presentando el monto total con el formato monetario apropiado. Esta funcionalidad resulta esencial para proporcionar transparencia al cliente sobre el valor exacto que recibirá como reembolso, fortaleciendo la confianza en el proceso automatizado.

La herramienta que construimos valida primero que los datos de entrada sean numéricos y coherentes, evitando errores en el cálculo. Una vez validados los parámetros, realiza la operación aritmética y presenta el resultado en un formato amigable que incluye el símbolo de moneda y dos decimales de precisión, siguiendo las mejores prácticas de presentación de información financiera.

#### Registro de Solicitud de Devolución

Implementamos esta herramienta como la culminación del proceso automatizado, registrando formalmente la solicitud de devolución en el sistema de EcoMarket. La función crea un registro persistente en el archivo CSV de solicitudes, asegurando trazabilidad completa del proceso.

El registro que generamos incluye metadatos esenciales como identificador de pedido, información del producto, motivo de devolución y timestamp de creación. Esta información alimenta los sistemas de logística inversa y control de calidad de la empresa, permitiendo análisis posteriores de tendencias y problemas recurrentes. Diseñamos el proceso para que sea atómico y consistente, garantizando que cada solicitud quede debidamente registrada sin duplicados ni pérdidas de información.

Nuestra implementación asegura que el directorio de destino exista antes de intentar escribir, creándolo automáticamente si es necesario. Esto previene errores comunes en sistemas de archivos y garantiza la robustez del proceso de registro. Una vez completado el registro, la herramienta confirma la operación al usuario con un mensaje claro que incluye los detalles de la solicitud y un número de seguimiento generado a partir del identificador del pedido.

## Diagramas de Arquitectura

!(https://github.com/claudia-pixel/IA_Generativa/blob/main/Taller%20final/Fase4/Contexto.png)

![Diagrama de contenedores](./Fase1/N1.png){width="380"}

### Diagrama de Flujo de Proceso

Creamos un diagrama detallado que muestra el flujo completo desde que un usuario envía una consulta hasta que recibe una respuesta. Este diagrama ilustra todas las decisiones que toma el agente, las herramientas que puede invocar, y cómo convergen los diferentes caminos para generar la respuesta final.

![Diagrama de Flujo del Proceso de Devolución](./Fase1/ProcDevol.png)

El diagrama muestra claramente la bifurcación inicial entre consultas generales que activan RAG y solicitudes de acción que invocan herramientas. Ilustra cómo cada herramienta tiene su propia lógica de validación y procesamiento, y cómo todas las rutas eventualmente convergen en la generación de una respuesta formateada que combina resultados de herramientas con contexto recuperado mediante RAG.



### Selección del Marco de Agentes: LangChain

Después de evaluar las opciones disponibles, seleccionamos LangChain como el framework principal para implementar nuestro agente de IA. Esta decisión la fundamentamos en varios criterios técnicos y prácticos que se alinean perfectamente con los requerimientos del proyecto EcoMarket.

#### Justificación de Nuestra Selección

Encontramos que LangChain ofrece un ecosistema maduro con amplia documentación, comunidad activa y abundantes recursos de aprendizaje. Esta característica resultó crucial para nuestro proyecto, que busca implementar soluciones de calidad profesional mientras mantiene una curva de aprendizaje razonable. La flexibilidad que descubrimos en la integración de modelos nos permitió utilizar tanto modelos locales como servicios en la nube, adaptándonos a diferentes escenarios de despliegue.

Apreciamos particularmente la arquitectura modular que implementa LangChain, basada en cadenas y componentes reutilizables que facilita la construcción incremental de funcionalidad. Esta modularidad resultó esencial para implementar el patrón RAG y posteriormente extenderlo con capacidades de agente. El soporte nativo para herramientas que encontramos en el framework incluye abstracciones específicas para definir y utilizar tools, permitiendo al agente decidir cuándo y cómo invocar funciones externas basándose en el contexto de la conversación.

Valoramos además las utilidades robustas que ofrece LangChain para manejar plantillas de prompts, gestionar el contexto de conversación, y optimizar el uso de tokens. Estas características mejoraron significativamente la calidad y eficiencia de las interacciones en nuestro sistema. Comparado con alternativas como LlamaIndex, que es excelente para casos de uso centrados en búsqueda y recuperación de información, LangChain nos ofreció mayor versatilidad para implementar agentes con capacidades de acción, lo cual era fundamental para nuestro proyecto específico.

### Selección del Modelo de Lenguaje: GPT-4o-mini

En nuestra implementación final, decidimos utilizar GPT-4o-mini de OpenAI como el modelo de lenguaje principal. Esta decisión representa una evolución respecto a implementaciones con modelos locales, priorizando la calidad de las respuestas y la capacidad de comprensión del lenguaje natural sobre la independencia de servicios externos.

Evaluamos que GPT-4o-mini ofrece un balance óptimo entre rendimiento, costo y capacidad. Como modelo optimizado de la familia GPT-4, proporciona comprensión avanzada del lenguaje natural en español, generación de respuestas coherentes y contextuales, y capacidad para seguir instrucciones complejas. La latencia de respuesta que observamos es aceptable para aplicaciones de atención al cliente, típicamente entre uno y tres segundos, lo cual mantiene una experiencia fluida para el usuario.

Configuramos el modelo con una temperatura de cero punto tres, lo que garantiza respuestas consistentes y determinísticas, minimizando la variabilidad innecesaria en un contexto de servicio al cliente donde la precisión y la confiabilidad son fundamentales. Esta configuración nos permite mantener un equilibrio entre creatividad en la formulación de respuestas y adherencia estricta a la información proporcionada en el contexto.

### Selección de Embeddings: OpenAI text-embedding-3-small

Para la generación de embeddings vectoriales, seleccionamos el modelo text-embedding-3-small de OpenAI. Esta elección la fundamentamos en la necesidad de obtener representaciones vectoriales de alta calidad que capturen efectivamente el significado semántico de los documentos corporativos.

Este modelo de embeddings nos proporciona vectores de dimensionalidad optimizada que balance between calidad de representación y eficiencia computacional. Observamos que text-embedding-3-small ofrece excelente rendimiento en tareas de similitud semántica, lo cual es crucial para el componente de recuperación en nuestra arquitectura RAG. La coherencia entre usar embeddings de OpenAI y el modelo de lenguaje GPT-4o-mini asegura una integración óptima en todo el pipeline de procesamiento.

### Selección de la Herramienta de Interfaz: Gradio

Para el despliegue de nuestra interfaz de usuario, seleccionamos Gradio en lugar de Streamlit. Esta decisión la basamos en varios factores que consideramos ventajosos para nuestro caso de uso específico.

Gradio nos ofrece una integración particularmente fluida con notebooks de Jupyter y Google Colab, entornos que utilizamos extensivamente durante el desarrollo. La simplicidad de su componente ChatInterface nos permitió crear una interfaz de chat conversacional con mínimas líneas de código, acelerando significativamente el proceso de prototipado. Además, encontramos que Gradio proporciona capacidades nativas de compartir la aplicación mediante un enlace público temporal, facilitando demostraciones rápidas sin necesidad de configurar infraestructura de despliegue.

La API de Gradio que experimentamos es intuitiva y requiere menos boilerplate que alternativas, lo que resulta ideal para proyectos académicos donde el enfoque debe estar en la funcionalidad del agente más que en detalles de implementación de la interfaz. El componente ChatInterface que utilizamos maneja automáticamente el estado de la conversación y el historial, liberándonos de tener que implementar esta lógica manualmente.

### Planificación del Flujo de Trabajo

Diseñamos el flujo de trabajo del agente siguiendo una arquitectura de decisión secuencial con puntos de validación en cada etapa. Este diseño asegura que las acciones automatizadas mantengan coherencia lógica y respeten las políticas empresariales.

Creamos un diagrama visual completo del flujo que muestra cómo el proceso inicia cuando el usuario envía un mensaje al sistema. El agente primero debe determinar la naturaleza de la solicitud, distinguiendo entre una consulta informativa que requiere búsqueda en la base de conocimientos o una solicitud de acción que necesita ejecutar una herramienta específica.

Diagrama de Flujo del Proceso de Devolución

Para consultas generales, nuestro sistema activa la cadena RAG, convirtiendo la pregunta en embeddings vectoriales y recuperando los documentos más relevantes del vectorstore. Estos documentos proporcionan el contexto necesario para que el modelo de lenguaje genere una respuesta precisa y fundamentada en información corporativa real. El proceso de recuperación que implementamos utiliza similitud coseno para identificar los tres documentos más relevantes, balanceando contexto suficiente con eficiencia en el procesamiento.

Para solicitudes de acción, diseñamos al agente para identificar patrones en el mensaje que indican la intención de iniciar un proceso de devolución. Esto puede incluir la detección del formato estructurado con punto y coma que indica parámetros específicos, o palabras clave como devolución, reembolso, o términos relacionados con problemas de productos como defectuoso o dañado.

Una vez identificada la herramienta apropiada, el agente que construimos valida que el mensaje contenga todos los parámetros necesarios en el formato correcto. Si la validación falla, retornamos un mensaje de error instructivo que guía al usuario sobre cómo formular su solicitud correctamente, manteniendo siempre un tono amable y orientado al servicio.

Con parámetros válidos, nuestro agente ejecuta la herramienta correspondiente. En el caso de verificación de elegibilidad, consultamos las políticas de devolución contra el motivo proporcionado. Para cálculos de reembolso, realizamos operaciones aritméticas con validación de tipos. Para registros, ejecutamos operaciones de escritura en archivos con manejo de errores robusto.

Finalmente, diseñamos que todas las respuestas se formateen de manera consistente y amigable antes de presentarse al usuario, manteniendo un tono profesional pero accesible que refleja los valores de EcoMarket. La respuesta final combina tanto el resultado de la herramienta ejecutada como contexto adicional recuperado mediante RAG, proporcionando una experiencia enriquecida que no solo resuelve la solicitud inmediata sino que educa al usuario sobre políticas y procedimientos relevantes.

### Consideraciones de Diseño

En nuestro diseño contemplamos varios aspectos críticos para asegurar la robustez del sistema. La separación entre lógica de negocio y lógica de presentación que implementamos facilita el mantenimiento futuro y permite evolucionar cada capa independientemente. El manejo explícito de errores en cada etapa que incorporamos previene fallos en cascada y asegura que el sistema degrade gracefully ante situaciones inesperadas.

Diseñamos la validación estricta de entradas para proteger contra inyección de datos maliciosos o mal formados, asegurando que solo datos correctamente estructurados lleguen a las funciones críticas del sistema. Esta capa de validación actúa como primera línea de defensa contra inputs inesperados que podrían causar comportamientos erróneos o comprometer la integridad de los datos.

También consideramos la escalabilidad en nuestro diseño. Aunque la implementación actual utiliza archivos CSV para persistencia, la arquitectura que construimos permite migrar fácilmente a bases de datos relacionales o sistemas de gestión documental sin modificar la lógica central del agente. Esta flexibilidad resulta fundamental para la evolución futura del sistema conforme crezcan los volúmenes de datos y las necesidades de concurrencia.
