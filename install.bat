@echo off
setlocal EnableDelayedExpansion
title Instalador de Markdown Printer

:: Check for Administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================
    echo   ESTE SCRIPT REQUIERE PRIVILEGIOS DE ADMINISTRADOR
    echo ============================================================
    echo Solicitando elevacion de privilegios...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================
echo      INSTALADOR DE IMPRESORA VIRTUAL MARKDOWN (Windows)
echo ============================================================
echo.

:: 1. Verify Python installation
echo [+] Verificando la instalacion de Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo encontrar Python en el PATH.
    echo Por favor, asegurese de tener Python instalado y la opcion
    echo "Add Python to PATH" seleccionada durante la instalacion.
    pause
    exit /b
)
echo [OK] Python detectado correctamente.
echo.

:: 2. Install dependencies
echo [+] Instalando dependencias de Python (pymupdf y pymupdf4llm)...
python -m pip install --upgrade pip
python -m pip install pymupdf pymupdf4llm
if %errorLevel% neq 0 (
    echo [ERROR] Hubo un problema al instalar las dependencias con pip.
    pause
    exit /b
)
echo [OK] Dependencias instaladas con exito.
echo.

:: 3. Setup Virtual Printer, Port and Shortcut using the Python Setup module
echo [+] Configurando Puerto TCP/IP local (127.0.0.1:9100), Impresora y Acceso directo...
python "%~dp0printer_server.py" --setup
if %errorLevel% neq 0 (
    echo [ERROR] Hubo un fallo al configurar la impresora en Windows.
    pause
    exit /b
)
echo [OK] Puerto, Impresora y Acceso directo creados con exito.
echo.

:: 4. Start the server background process now
echo [+] Iniciando el servidor de impresion en segundo plano...
:: Kill any existing running process of printer_server.py to avoid port in use
taskkill /f /im pythonw.exe >nul 2>&1
start "" pythonw.exe "%~dp0printer_server.py"
echo [OK] Servidor de impresion iniciado exitosamente en 127.0.0.1:9100.
echo.

echo ============================================================
echo   ¡INSTALACION COMPLETADA CON EXITO!
echo ============================================================
echo.
echo Ya puedes imprimir cualquier documento seleccionando la
echo impresora "Markdown Printer" desde cualquier aplicacion.
echo.
echo Los archivos se guardaran en la carpeta seleccionada y se
echo abriran automaticamente en Notepad++.
echo.
echo Puedes ver los registros de eventos en:
echo %USERPROFILE%\.md_printer.log
echo.
pause
