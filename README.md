# Markdown Printer (Impresora Virtual Markdown para Windows)

Una herramienta elegante y automatizada que se instala como una impresora virtual en Windows y convierte cualquier documento que imprimas en un formato **Markdown (.md) estructurado**, extrayendo las imágenes en paralelo de forma local.

---

## 🚀 Características

* **Sin controladores de terceros complejos:** Utiliza el controlador nativo de Windows `Microsoft Print to PDF` redirigido a un puerto TCP/IP local (`127.0.0.1:9100`), lo que garantiza un funcionamiento 100% estable, rápido y compatible con Windows 10/11.
* **Conversión de Alta Calidad:** Utiliza el potente motor de `PyMuPDF` y `pymupdf4llm` para extraer títulos, encabezados, listas, tablas y texto fluido con alta fidelidad y velocidad.
* **Extracción de Imágenes:** Si el documento contiene imágenes o gráficos, se extraen automáticamente en una subcarpeta paralela `imagenes/` y se insertan con sus respectivas referencias relativas `![](imagenes/imagen.png)` dentro del archivo Markdown.
* **Estructura Organizada por Impresión:** Crea una carpeta dedicada por cada trabajo de impresión para mantener el archivo Markdown y sus recursos multimedia perfectamente ordenados.
* **Cuadro de diálogo Nativo (Guardar como):** Al imprimir, se abrirá automáticamente un cuadro de diálogo flotante en primer plano para que elijas dónde guardar el archivo, proponiendo un nombre inteligente extraído del título del documento o basado en la fecha y hora.
* **Ruta de OneDrive Predeterminada:** Está preconfigurado para abrir por defecto tu carpeta de OneDrive:
  `C:\Users\jmenar\One Drive PERSONAL\OneDrive - TORNILLERIA Y SERVICIOS S.L.U\TORSESA 2026`
  *(Si no existe, utiliza de forma inteligente tu carpeta de usuario o documentos como alternativa)*.
* **Apertura Automática en Notepad++:** Una vez guardado con éxito, el archivo `.md` estructurado se abrirá automáticamente de inmediato en **Notepad++** para que puedas visualizarlo, editarlo o copiarlo.
* **Ejecución Invisible en Segundo Plano:** El servidor de impresión se inicia de manera silenciosa al arrancar Windows (Startup) sin molestas ventanas negras de consola.

---

## 🛠️ Requisitos Previos

Antes de realizar la instalación, asegúrate de cumplir con lo siguiente en tu sistema Windows:

1. **Python 3.x instalado** y agregado al `PATH` del sistema (asegúrate de marcar la casilla *"Add Python to PATH"* durante la instalación de Python).
2. **Notepad++ instalado** (en su ubicación predeterminada en `C:\Program Files\Notepad++\notepad++.exe` o similar).
3. **Microsoft Print to PDF** habilitado en Windows (viene activo por defecto en Windows 10 y 11).

---

## 📦 Instalación (Un Solo Clic)

1. Descarga o clona este repositorio en una carpeta permanente de tu computadora (por ejemplo, `C:\md_printer` o dentro de tu OneDrive).
2. Haz clic derecho sobre el archivo **`install.bat`** y selecciona **"Ejecutar como Administrador"**.
3. El instalador se encargará de:
   * Verificar la presencia de Python en tu sistema.
   * Instalar y actualizar las librerías necesarias (`pymupdf`, `pymupdf4llm`).
   * Configurar un puerto de red de impresión estándar en `127.0.0.1` en el puerto `9100`.
   * Crear la impresora virtual **"Markdown Printer"** vinculada a este puerto.
   * Configurar el inicio automático silencioso para que la impresora esté siempre lista cuando enciendas tu computadora.
   * Iniciar el servicio en segundo plano de inmediato.

---

## 📖 Instrucciones de Uso

¡Utilizarlo es sumamente sencillo!

1. Abre cualquier documento que desees convertir (un archivo PDF, un documento de Word, una página web en el navegador, una hoja de Excel, etc.).
2. Presiona `Ctrl + P` (o ve al menú de Imprimir) y selecciona la impresora **`Markdown Printer`**.
3. Haz clic en **Imprimir**.
4. En pocos segundos, aparecerá la ventana nativa de Windows pidiéndote que elijas el nombre y la ubicación de tu archivo Markdown (apuntando por defecto a tu carpeta de OneDrive `TORSESA 2026`).
5. Al hacer clic en **Guardar**, el programa convertirá el documento, organizará las imágenes, creará su carpeta correspondiente, y **abrirá el archivo Markdown listo en Notepad++**.

---

## 📝 Registro de Eventos (Logs)

Si alguna vez necesitas verificar el estado del servidor, comprobar errores o realizar un seguimiento de los documentos impresos, el programa escribe registros detallados en un archivo de log local ubicado en tu carpeta de usuario:

📁 Path del Log: `C:\Usuarios\<Tu-Usuario>\.md_printer.log`

Puedes abrir este archivo en cualquier momento para ver todo el historial de impresión y depuración.
