# DocSage 🧙‍♂️ - Documentación del Proyecto

## Descripción
DocSage es una aplicación de chat inteligente construida con Streamlit que permite cargar documentos y hacer preguntas sobre su contenido usando IA generativa (OpenAI GPT-4).

## Estructura del Proyecto
```
GENERATIVE_AI_ICESI/
├── controller/
│   ├── db.py                 # Operaciones de base de datos SQLite (CRUD)
│   └── vector_functions.py   # Funciones de procesamiento de documentos y IA
├── db/
│   ├── doc_sage.sqlite       # Base de datos SQLite
│   └── relational_db.py      # Script de creación de tablas (inicialización)
├── front/
│   └── chats.py             # Interfaz de usuario Streamlit
├── venv/                    # Entorno virtual de Python
├── .env                     # Variables de entorno (crear manualmente)
├── env_template.txt         # Plantilla de variables de entorno
└── requirements.txt         # Dependencias de Python
```

### Archivos de Base de Datos
- **`db/relational_db.py`**: Script de **inicialización** que crea las tablas (`chat`, `messages`, `sources`)
- **`controller/db.py`**: Módulo de **operaciones** que permite crear, leer, actualizar y eliminar datos

## Instalación y Configuración

### Prerrequisitos
- Python 3.13+
- pip (gestor de paquetes de Python)
- Cuenta de OpenAI con API key

### Paso 1: Clonar/Descargar el Proyecto
```bash
# Si tienes el proyecto en Git
git clone <repository-url>
cd GENERATIVE_AI_ICESI

# O si ya tienes los archivos, navega al directorio
cd /ruta/a/tu/proyecto/GENERATIVE_AI_ICESI
```

### Paso 2: Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate

# En Windows:
# venv\Scripts\activate
```

### Paso 3: Instalar Dependencias
```bash
# Asegúrate de que el entorno virtual esté activado
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

#### Opción A: Usar archivo .env (Recomendado)
```bash
# Copiar plantilla
cp env_template.txt .env

# Editar el archivo .env con tu editor preferido
nano .env
# o
code .env
# o
vim .env
```

En el archivo `.env`, reemplaza `your_openai_api_key_here` con tu API key real:
```
OPENAI_API_KEY=sk-proj-tu_api_key_real_aqui
DATABASE_URL=sqlite:///doc_sage.sqlite
DEBUG=True
```

#### Opción B: Configurar variable de entorno directamente
```bash
# Para la sesión actual
export OPENAI_API_KEY="sk-proj-tu_api_key_real_aqui"

# Para hacerlo permanente, agregar al archivo ~/.bashrc o ~/.zshrc
echo 'export OPENAI_API_KEY="sk-proj-tu_api_key_real_aqui"' >> ~/.bashrc
source ~/.bashrc
```

### Paso 5: Crear Base de Datos
```bash
# Navegar al directorio db
cd db

# Ejecutar script de creación de tablas
python relational_db.py

# Volver al directorio raíz
cd ..
```

### Paso 6: Verificar Instalación
```bash
# Verificar que las dependencias están instaladas
python -c "import streamlit, langchain_chroma, langchain_openai; print('✅ Todas las dependencias están instaladas')"

# Verificar configuración de OpenAI
python -c "from controller.vector_functions import llm; print('✅ Configuración de OpenAI correcta')"

# Verificar base de datos (usar módulo de operaciones CRUD)
python -c "from controller.db import list_chats; print('✅ Base de datos conectada:', list_chats())"
```

**Nota importante**: 
- `relational_db.py` **crea** las tablas (se ejecuta una vez)
- `controller.db` **usa** las tablas para operaciones (se importa constantemente)

## Ejecución

### Ejecutar la Aplicación
```bash
# Asegúrate de estar en el directorio raíz del proyecto
# y que el entorno virtual esté activado

source venv/bin/activate
streamlit run front/chats.py
```

### Acceder a la Aplicación
- **URL Local**: http://localhost:8501
- **URL de Red**: http://tu-ip:8501

## Uso de la Aplicación

### Funcionalidades Principales
1. **Crear Chat**: Ingresa un título y crea una nueva conversación
2. **Cargar Documentos**: Sube archivos (.txt, .pdf, .docx, .csv, .html, .md)
3. **Hacer Preguntas**: Pregunta sobre el contenido de los documentos cargados
4. **Historial**: Ve conversaciones anteriores

### Tipos de Archivos Soportados
- `.txt` - Archivos de texto plano
- `.pdf` - Documentos PDF
- `.docx` - Documentos de Word
- `.csv` - Archivos CSV
- `.html` - Páginas web HTML
- `.md` - Archivos Markdown

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'langchain_chroma'"
**Causa**: No estás usando el entorno virtual correcto.
**Solución**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Error: "ImproperlyConfigured: Set the OPENAI_API_KEY environment variable"
**Causa**: La API key de OpenAI no está configurada.
**Solución**:
```bash
# Verificar que el archivo .env existe y tiene la API key
cat .env

# O configurar directamente
export OPENAI_API_KEY="tu_api_key_aqui"
```

### Error: "OperationalError: no such table: chat"
**Causa**: Las tablas de la base de datos no existen.
**Solución**:
```bash
# Opción 1: Usar el script de inicialización
cd db
python relational_db.py
cd ..

# Opción 2: Usar el script de automatización
./setup.sh db
```

### Error: "unable to open database file"
**Causa**: Ruta incorrecta de la base de datos.
**Solución**: Verificar que el archivo `controller/db.py` tenga la ruta correcta:
```python
return sqlite3.connect("db/doc_sage.sqlite")
```

## Comandos Útiles

### Gestión del Entorno Virtual
```bash
# Activar entorno virtual
source venv/bin/activate

# Desactivar entorno virtual
deactivate

# Ver paquetes instalados
pip list

# Actualizar paquetes
pip install --upgrade -r requirements.txt
```

### Gestión de la Base de Datos
```bash
# Crear/inicializar tablas (ejecutar script de inicialización)
cd db
python relational_db.py
cd ..

# Ver tablas existentes
sqlite3 db/doc_sage.sqlite ".tables"

# Ver estructura de una tabla
sqlite3 db/doc_sage.sqlite ".schema chat"

# Ejecutar consulta SQL
sqlite3 db/doc_sage.sqlite "SELECT * FROM chat;"

# Probar operaciones CRUD (usar módulo de operaciones)
python -c "from controller.db import list_chats, create_chat; print(list_chats())"
```

### Debugging
```bash
# Verificar variables de entorno
echo $OPENAI_API_KEY

# Verificar Python path
python -c "import sys; print(sys.path)"

# Verificar instalación de paquetes específicos
python -c "import langchain_chroma; print(langchain_chroma.__version__)"
```

## Desarrollo

### Estructura de Archivos Importantes
- `front/chats.py`: Interfaz de usuario principal
- `controller/vector_functions.py`: Lógica de procesamiento de documentos y IA
- `controller/db.py`: Operaciones de base de datos
- `db/relational_db.py`: Script de inicialización de la base de datos

### Agregar Nuevas Funcionalidades
1. Modifica los archivos en `controller/` para la lógica de negocio
2. Actualiza `front/chats.py` para la interfaz de usuario
3. Si necesitas nuevas tablas, modifica `db/relational_db.py`

### Testing
```bash
# Probar conexión a OpenAI
python -c "from controller.vector_functions import llm; print(llm.invoke('Hola').content)"

# Probar base de datos
python -c "from controller.db import create_chat, list_chats; create_chat('Test'); print(list_chats())"
```

## Notas Importantes

### Seguridad
- **NUNCA** compartas tu API key de OpenAI
- El archivo `.env` está en `.gitignore` para proteger información sensible
- Mantén tu API key segura y no la incluyas en commits

### Rendimiento
- Para mejor rendimiento en macOS, instala Watchdog:
```bash
xcode-select --install
pip install watchdog
```

### Limitaciones
- La aplicación usa OpenAI GPT-4o-mini (modelo económico)
- Los documentos se procesan en chunks de 1000 caracteres
- La base de datos SQLite es local (no escalable para múltiples usuarios)

## Soporte

Si encuentras problemas:
1. Verifica que sigues todos los pasos de instalación
2. Revisa la sección de solución de problemas
3. Asegúrate de que todas las dependencias están instaladas
4. Verifica que tu API key de OpenAI es válida y tiene créditos

---

**Última actualización**: Octubre 2024
**Versión**: 1.0.0



source venv/bin/activate
streamlit run front/chats.py