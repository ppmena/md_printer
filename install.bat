@echo off
setlocal EnableDelayedExpansion
title Markdown Printer Installer

:: Check for Administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ============================================================
    echo   THIS SCRIPT REQUIRES ADMINISTRATIVE PRIVILEGES
    echo ============================================================
    echo Requesting privilege elevation...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo ============================================================
echo      MARKDOWN VIRTUAL PRINTER INSTALLER (Windows)
echo ============================================================
echo.

:: 1. Verify Python installation
echo [+] Verifying Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please make sure you have Python installed and the option
    echo "Add Python to PATH" selected during installation.
    pause
    exit /b
)
echo [OK] Python detected successfully.
echo.

:: 2. Install dependencies
echo [+] Installing Python dependencies (pymupdf and pymupdf4llm)...
python -m pip install --upgrade pip
python -m pip install pymupdf pymupdf4llm
if %errorLevel% neq 0 (
    echo [ERROR] An issue occurred while installing dependencies with pip.
    pause
    exit /b
)
echo [OK] Dependencies installed successfully.
echo.

:: 3. Setup Virtual Printer, Port and Shortcut using the Python Setup module
echo [+] Configuring Windows TCP/IP Port (127.0.0.1:9100), Printer, and Shortcut...
python "%~dp0printer_server.py" --setup
if %errorLevel% neq 0 (
    echo [ERROR] Failed to configure the printer in Windows.
    pause
    exit /b
)
echo [OK] Port, Printer, and Startup shortcut configured successfully.
echo.

:: 4. Start the server background process now
echo [+] Starting the print server in the background...
:: Kill any existing running process of printer_server.py to avoid port in use
taskkill /f /im pythonw.exe >nul 2>&1
start "" pythonw.exe "%~dp0printer_server.py"
echo [OK] Print server successfully started on 127.0.0.1:9100.
echo.

echo ============================================================
echo   INSTALLATION COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo You can now print any document by selecting the
echo "Markdown Printer" from any application.
echo.
echo The files will be saved in your chosen folder and will
echo automatically open in Notepad++.
echo.
echo You can view the event logs at:
echo %USERPROFILE%\.md_printer.log
echo.
pause
