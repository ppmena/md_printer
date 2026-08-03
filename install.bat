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

:: 3. Setup Virtual Printer and Port using PowerShell (Single-line execution to avoid command prompt caret parser bugs)
echo [+] Configurando Puerto TCP/IP local (127.0.0.1:9100) e Impresora...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$PN='MarkdownPrinterPort'; $PR='Markdown Printer'; $DR='Microsoft Print to PDF'; Write-Host ' - Verificando puerto...'; if (!(Get-PrinterPort -Name $PN -EA SilentlyContinue)) { Write-Host ' - Creando puerto TCP/IP local en 127.0.0.1 (Puerto 9100)...'; Add-PrinterPort -Name $PN -PrinterHostAddress '127.0.0.1' } else { Write-Host ' - El puerto ya existe.' }; Write-Host ' - Verificando controlador (driver)...'; if (!(Get-PrinterDriver -Name $DR -EA SilentlyContinue)) { Write-Error 'El controlador Microsoft Print to PDF no esta instalado. Por favor, asegurese de tener activa la caracteristica de Windows: Microsoft Print to PDF.'; exit 1 }; Write-Host ' - Verificando impresora...'; if (!(Get-Printer -Name $PR -EA SilentlyContinue)) { Write-Host ' - Creando impresora virtual: Markdown Printer...'; Add-Printer -Name $PR -DriverName $DR -PortName $PN } else { Write-Host ' - La impresora ya existe.' }"
if %errorLevel% neq 0 (
    echo [ERROR] Hubo un fallo al configurar la impresora en Windows.
    pause
    exit /b
)
echo [OK] Puerto e Impresora configurados correctamente.
echo.

:: 4. Create startup shortcut (Single-line execution to avoid command prompt caret parser bugs)
echo [+] Configurando inicio automatico con Windows...
set "SCRIPT_PATH=%~dp0printer_server.py"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$WshShell = New-Object -ComObject WScript.Shell; $ShortcutPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\MarkdownPrinter.lnk'; $Shortcut = $WshShell.CreateShortcut($ShortcutPath); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '\"%SCRIPT_PATH%\"'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.WindowStyle = 7; $Shortcut.Description = 'Servidor de Impresion Markdown'; $Shortcut.Save()"
echo [OK] Acceso directo de inicio automatico creado.
echo.

:: 5. Start the server background process now
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
