#!/bin/bash

# Script de inicio rápido para el Simulador SNI Ecuador
# Uso: bash quickstart.sh

echo "╔════════════════════════════════════════════════════════╗"
echo "║     SNI Ecuador - Simulador de Sistema de Potencia     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Obtener el directorio actual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -q -r requirements.txt

# Ejecutar la aplicación
echo ""
echo "Iniciando aplicación Streamlit..."
echo "URL: http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener la aplicación"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run app.py
