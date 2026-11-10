@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando el entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo No se pudo crear el entorno. Verifica que Python este instalado.
        pause
        exit /b 1
    )
)

echo Comprobando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -c "from myapp.views import asegurar_archivo_donaciones, DONACIONES_FILE; asegurar_archivo_donaciones(); print('Archivo de donaciones:', DONACIONES_FILE.resolve())"

echo Iniciando Huellitas del Valle...
".venv\Scripts\python.exe" manage.py runserver
pause
