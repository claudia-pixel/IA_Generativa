## Fase 2: Implementación y Conexión de Componentes

### Introducción a la Implementación

Transformamos el diseño conceptual en código funcional, integrando todos los componentes en un sistema cohesivo. Esta fase representa el trabajo técnico central del proyecto donde materializamos las decisiones arquitectónicas en una implementación real y funcional. Organizamos nuestro código siguiendo principios de separación de responsabilidades y modularidad para facilitar el mantenimiento y la extensibilidad futura.

### Estructura del Proyecto

Organizamos el proyecto siguiendo una estructura lógica que refleja las diferentes capas de la arquitectura. Creamos un directorio principal para datos de entrada que contiene todos los archivos corporativos, un directorio para el vectorstore que almacena los índices generados, y un directorio de salida para las solicitudes de devolución registradas. Esta organización facilita la gestión de archivos y clarifica las responsabilidades de cada componente del sistema.

### Configuración del Entorno

Configuramos el entorno de ejecución para trabajar tanto en Google Colab como en entornos locales. Implementamos la carga de variables de entorno mediante dotenv, lo que permite gestionar de manera segura credenciales sensibles como la API key de OpenAI. Esta aproximación separa la configuración del código, siguiendo las mejores prácticas de desarrollo de software y facilitando el despliegue en diferentes entornos sin necesidad de modificar el código fuente.

Establecimos la configuración de la API key de OpenAI como paso crítico en la inicialización del sistema. Aunque en el notebook incluimos la key directamente para propósitos de demostración, recomendamos fuertemente utilizar variables de entorno en producción para mantener la seguridad de las credenciales. Configuramos también las rutas de directorios de manera relativa, permitiendo que el sistema funcione independientemente de la ubicación específica de instalación.

### Gestión de Dependencias

Instalamos cuidadosamente las dependencias necesarias, especificando versiones exactas para garantizar reproducibilidad. Incluimos LangChain y sus módulos de integración con OpenAI, las bibliotecas para procesamiento de diferentes formatos de archivo, y Gradio para la interfaz de usuario. Esta selección de dependencias representa un ecosistema completo que habilita todas las funcionalidades requeridas por nuestro agente.

Priorizamos el uso de versiones estables y bien documentadas de cada biblioteca, evitando versiones en desarrollo que podrían introducir inestabilidad. La instalación que configuramos incluye también dependencias para procesamiento de documentos no estructurados, permitiendo extraer texto de PDFs y archivos Excel de manera robusta.

### Implementación de las Herramientas

Implementamos las tres herramientas centrales como funciones Python independientes, cada una con su propia lógica de validación y procesamiento. Diseñamos estas funciones para ser puras en el sentido de que dado el mismo input siempre producen el mismo output, sin efectos secundarios inesperados salvo la escritura controlada en archivos CSV para el caso del registro de solicitudes.

La herramienta de verificación de elegibilidad que desarrollamos parsea la entrada estructurada, extrae los cuatro campos requeridos, y evalúa el motivo contra una lista predefinida de motivos válidos. Implementamos manejo de excepciones robusto para capturar errores de formato y retornar mensajes instructivos que guían al usuario hacia el formato correcto. Esta aproximación pedagógica en el manejo de errores mejora significativamente la experiencia del usuario al proporcionar retroalimentación accionable.

Para el cálculo de reembolsos, construimos una función que valida tipos de datos antes de realizar operaciones aritméticas. Convertimos explícitamente la cantidad a entero y el precio a flotante, capturando excepciones de conversión que podrían ocurrir con datos mal formados. El formato de salida que implementamos incluye el símbolo de moneda y dos decimales de precisión, proporcionando una presentación profesional del resultado.

La función de registro que creamos asegura primero la existencia del directorio de destino, utilizando la función makedirs con el flag exist_ok para evitar errores si el directorio ya existe. Abrimos el archivo CSV en modo append para preservar registros anteriores, y utilizamos el módulo csv de Python para garantizar el formato correcto de las entradas. Esta implementación asegura la integridad de los datos incluso en escenarios de alta concurrencia donde múltiples solicitudes podrían intentar escribir simultáneamente.

### Construcción del Sistema RAG

Construimos el sistema RAG implementando primero la funcionalidad de carga y procesamiento de documentos. Desarrollamos una función que recorre el directorio de datos, identificando el tipo de cada archivo por su extensión y utilizando el loader apropiado de LangChain. Esta aproximación genérica nos permite agregar nuevos tipos de archivo en el futuro simplemente extendiendo la lógica de detección de tipos.

El proceso de carga que implementamos maneja diferentes formatos de documento de manera unificada, convirtiendo todo a la estructura Document de LangChain que estandariza la representación de contenido textual con metadatos. Aplicamos un text splitter recursivo que divide los documentos en chunks de mil caracteres con doscientos caracteres de overlap, balanceando el tamaño manejable para el modelo con la preservación de contexto entre fragmentos adyacentes.

Generamos los embeddings utilizando el modelo text-embedding-3-small de OpenAI, que produce vectores de alta calidad capturando el significado semántico del texto. Almacenamos estos embeddings en un vectorstore FAISS, una biblioteca eficiente para búsqueda de similitud en espacios vectoriales de alta dimensión. FAISS nos proporciona capacidades de búsqueda extremadamente rápidas incluso con miles de documentos, utilizando algoritmos de indexación optimizados.

Implementamos la funcionalidad de persistencia del vectorstore, guardándolo localmente después de su creación inicial. En ejecuciones subsecuentes, cargamos el vectorstore existente en lugar de regenerarlo, ahorrando tiempo y costos de API. Esta optimización resulta particularmente importante considerando que la generación de embeddings consume créditos de OpenAI y puede tomar varios minutos para colecciones grandes de documentos.

### Configuración del Modelo de Lenguaje

Configuramos GPT-4o-mini como nuestro modelo de lenguaje, estableciendo parámetros cuidadosamente seleccionados para optimizar el comportamiento del sistema. Fijamos la temperatura en cero punto tres, un valor que encontramos proporciona el balance ideal entre consistencia y naturalidad en las respuestas. Valores más bajos producirían respuestas excesivamente mecánicas, mientras que valores más altos introducirían variabilidad indeseable para un contexto de servicio al cliente.

Creamos un template de prompt estructurado que define claramente el rol del agente como asistente de atención al cliente de EcoMarket. El prompt que diseñamos instruye explícitamente al modelo para usar el contexto proporcionado, responder en español claro y amable, y mantener un tono profesional pero accesible. Esta ingeniería de prompt resultó crucial para obtener respuestas consistentes con la identidad de marca de EcoMarket y las expectativas de calidad del servicio.

### Integración de Retriever y Cadena RAG

Configuramos el retriever con un parámetro k de tres, indicando que debe recuperar los tres documentos más relevantes para cada consulta. Experimentamos con diferentes valores de k y encontramos que tres proporciona suficiente contexto sin abrumar al modelo con información redundante. Esta configuración permite al modelo tener una vista comprehensiva del conocimiento relevante mientras mantiene respuestas concisas y enfocadas.

Ensamblamos la cadena RAG utilizando el componente RetrievalQA de LangChain, que orquesta el flujo completo de recuperación y generación. Esta cadena que construimos primero invoca al retriever para obtener documentos relevantes, luego formatea estos documentos junto con la pregunta del usuario según nuestro template de prompt, y finalmente envía todo al modelo de lenguaje para generar la respuesta. La automatización de este flujo por LangChain nos libera de manejar manualmente los detalles de integración entre componentes.

### Implementación de la Lógica de Decisión del Agente

Desarrollamos la función principal de chat que implementa la lógica de decisión del agente. Esta función que creamos primero detecta si el mensaje del usuario contiene el carácter punto y coma, que utilizamos como indicador de que el usuario intenta ejecutar una herramienta con parámetros estructurados. Si detectamos este formato, analizamos las palabras clave en el mensaje para determinar qué herramienta específica invocar.

Implementamos una lógica de cascada donde primero verificamos si el mensaje contiene la palabra devolución, en cuyo caso invocamos la herramienta de registro. Si no, verificamos la presencia de reembolso para invocar la calculadora. En ausencia de ambas palabras clave, asumimos que se trata de una verificación de elegibilidad. Esta aproximación pragmática funciona bien en la práctica aunque podría refinarse con técnicas más sofisticadas de clasificación de intenciones para casos de uso más complejos.

Para mensajes que no contienen el formato estructurado, el agente que construimos directamente invoca la cadena RAG, asumiendo que se trata de una consulta informativa general. Esta dualidad en el procesamiento, herramientas para acciones y RAG para información, constituye el núcleo de nuestra arquitectura híbrida que combina recuperación de conocimiento con capacidad de ejecución.

### Manejo de Respuestas y Errores

Implementamos manejo de errores en múltiples niveles del sistema. Cada herramienta incluye bloques try-except que capturan excepciones de parsing y conversión de tipos, retornando mensajes de error amigables en lugar de permitir que excepciones no manejadas lleguen al usuario. Esta aproximación defensive programming asegura que el sistema nunca se rompa completamente ante inputs inesperados.

Formateamos todas las respuestas con emojis y estructura clara, mejorando la legibilidad y haciendo la interacción más amigable. Los mensajes de éxito utilizamos emojis positivos como checkmarks verdes, mientras que los errores utilizan símbolos de advertencia en amarillo o rojo. Esta codificación visual ayuda a los usuarios a interpretar rápidamente el resultado de sus solicitudes.

### Implementación de la Interfaz con Gradio

Desplegamos la interfaz de usuario utilizando el componente ChatInterface de Gradio, que nos proporciona una interfaz de chat completa con mínima configuración. Configuramos el título y descripción de la aplicación para que los usuarios comprendan inmediatamente el propósito y capacidades del sistema. El ChatInterface que utilizamos maneja automáticamente el historial de conversación, mostrando los mensajes previos en un formato de chat familiar que mejora significativamente la experiencia del usuario.

Lanzamos la aplicación con el método launch de Gradio, que inicia un servidor web local y proporciona una URL para acceder a la interfaz. En entornos como Google Colab, Gradio además genera un enlace público temporal que permite compartir la aplicación con otras personas sin necesidad de configuración de red compleja. Esta facilidad de compartir resultó invaluable durante nuestras fases de testing y demostración.

### Evaluación del Comportamiento

Probamos exhaustivamente el sistema con diferentes tipos de consultas para verificar su capacidad de discernimiento. Ejecutamos pruebas con consultas generales sobre productos, verificamos que la detección de formato estructurado funcionara correctamente, y validamos que cada herramienta se ejecutara apropiadamente según el contexto.

Documentamos varios casos de prueba representativos. Para consultas generales como preguntar sobre productos disponibles, verificamos que el sistema recuperara información relevante de los documentos corporativos y la presentara de manera coherente. Para verificaciones de elegibilidad, probamos tanto casos que deberían aprobar como casos que deberían rechazar, confirmando que la lógica de decisión funcionara correctamente. Para cálculos de reembolso, validamos la precisión aritmética y el formato de presentación. Para registros de devolución, inspeccionamos manualmente el archivo CSV generado para confirmar que los datos se persistieran correctamente.

Los resultados que obtuvimos demostraron que el agente identifica correctamente cuándo usar herramientas versus RAG, maneja errores de formato gracefully proporcionando retroalimentación útil, provee respuestas contextuales relevantes, y mantiene consistencia en el tono de comunicación. Estos resultados nos dieron confianza en que el sistema está listo para demostración y evaluación en escenarios más cercanos a producción.

### Integración de Componentes

Logramos integrar todos los componentes en un flujo cohesivo donde el usuario envía un mensaje, el sistema detecta la presencia de formato de herramienta, ejecuta la herramienta correspondiente si aplica, siempre ejecuta RAG para proporcionar contexto adicional, combina ambas respuestas de manera coherente, y registra la interacción. Esta arquitectura híbrida que implementamos asegura que el usuario siempre reciba tanto la acción solicitada como información contextual relevante, maximizando la utilidad de cada interacción y proporcionando una experiencia rica e informativa.
