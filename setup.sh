#!/bin/bash
# DocSage - Comandos Rápidos
# Este archivo contiene comandos útiles para gestionar el proyecto DocSage

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}DocSage - Comandos Rápidos${NC}"
echo "================================"

# Función para mostrar ayuda
show_help() {
    echo -e "${YELLOW}Comandos disponibles:${NC}"
    echo "  setup     - Configurar proyecto desde cero"
    echo "  install   - Instalar dependencias"
    echo "  env       - Configurar variables de entorno"
    echo "  db        - Crear/inicializar base de datos"
    echo "  run       - Ejecutar aplicación"
    echo "  test      - Probar configuración"
    echo "  clean     - Limpiar archivos temporales"
    echo "  help      - Mostrar esta ayuda"
}

# Función para configurar proyecto desde cero
setup_project() {
    echo -e "${GREEN}Configurando proyecto DocSage...${NC}"
    
    # Crear entorno virtual
    echo "Creando entorno virtual..."
    python -m venv venv
    
    # Activar entorno virtual
    echo "Activando entorno virtual..."
    source venv/bin/activate
    
    # Instalar dependencias
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    
    # Configurar variables de entorno
    echo "Configurando variables de entorno..."
    if [ ! -f .env ]; then
        cp env_template.txt .env
        echo -e "${YELLOW}IMPORTANTE: Edita el archivo .env y agrega tu API key de OpenAI${NC}"
    fi
    
    # Crear base de datos (ejecutar script de inicialización)
    echo "Creando base de datos..."
    cd db
    python relational_db.py  # Script que crea las tablas
    cd ..
    
    echo -e "${GREEN}✅ Proyecto configurado correctamente${NC}"
}

# Función para instalar dependencias
install_deps() {
    echo -e "${GREEN}Instalando dependencias...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
}

# Función para configurar variables de entorno
setup_env() {
    echo -e "${GREEN}Configurando variables de entorno...${NC}"
    if [ ! -f .env ]; then
        cp env_template.txt .env
        echo -e "${YELLOW}Archivo .env creado. Edítalo con tu API key de OpenAI${NC}"
    else
        echo -e "${YELLOW}Archivo .env ya existe${NC}"
    fi
}

# Función para crear base de datos
setup_db() {
    echo -e "${GREEN}Creando base de datos...${NC}"
    cd db
    python relational_db.py  # Script que crea las tablas
    cd ..
    echo -e "${GREEN}✅ Base de datos creada${NC}"
}

# Función para ejecutar aplicación
run_app() {
    echo -e "${GREEN}Ejecutando DocSage...${NC}"
    source venv/bin/activate
    streamlit run front/chats.py
}

# Función para probar configuración
test_config() {
    echo -e "${GREEN}Probando configuración...${NC}"
    source venv/bin/activate
    
    echo "Probando dependencias..."
    python -c "import streamlit, langchain_chroma, langchain_openai; print('✅ Dependencias OK')" || echo -e "${RED}❌ Error en dependencias${NC}"
    
    echo "Probando configuración OpenAI..."
    python -c "from controller.vector_functions import llm; print('✅ OpenAI OK')" || echo -e "${RED}❌ Error en OpenAI${NC}"
    
    echo "Probando base de datos..."
    python -c "from controller.db import list_chats; print('✅ Base de datos OK:', list_chats())" || echo -e "${RED}❌ Error en base de datos${NC}"  # Módulo que usa las tablas
}

# Función para limpiar archivos temporales
clean_project() {
    echo -e "${GREEN}Limpiando archivos temporales...${NC}"
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    echo -e "${GREEN}✅ Archivos temporales eliminados${NC}"
}

# Procesar argumentos
case "$1" in
    setup)
        setup_project
        ;;
    install)
        install_deps
        ;;
    env)
        setup_env
        ;;
    db)
        setup_db
        ;;
    run)
        run_app
        ;;
    test)
        test_config
        ;;
    clean)
        clean_project
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Comando no reconocido: $1${NC}"
        show_help
        ;;
esac
