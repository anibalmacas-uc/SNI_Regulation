@echo off
REM Script de inicio rápido para Windows
REM Simulador SNI Ecuador

echo.
echo ╔═════════════════════════════════════════════════════╗
echo ║  SNI Ecuador - Simulador de Sistema de Potencia     ║
echo ╚═════════════════════════════════════════════════════╝
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -q -r requirements.txt

REM Ejecutar
echo.
echo Iniciando aplicación Streamlit...
echo URL: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener la aplicación
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

streamlit run app.py

pause
