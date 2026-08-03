# Markdown Printer (Virtual Markdown Printer for Windows)

An elegant, automated tool that installs as a virtual printer in Windows and automatically converts any printed document into a **structured Markdown (.md)** format, extracting images in parallel and saving everything locally.

---

## 🚀 Features

* **Driverless Setup:** Built using Windows' native `Microsoft Print to PDF` driver redirected to a standard local TCP/IP Port (`127.0.0.1:9100`), ensuring 100% stability, speed, and compatibility on Windows 10/11.
* **High-Fidelity Conversion:** Leverages `PyMuPDF` and `pymupdf4llm` layout-aware extraction to parse titles, headers, bullet lists, simple tables, and body paragraphs seamlessly.
* **Image Extraction:** Embedded images and drawings are automatically extracted into a parallel `images/` directory and referenced correctly with portable relative Markdown image links (`![](images/img-X-Y.png)`).
* **Dedicated Document Folders:** Keeps your workspace tidy by creating a dedicated directory per print job to store the `.md` file and its companion media assets together.
* **Native Foreground Save Dialog:** When you print, a native Windows save file dialog pops up directly on top of your windows, allowing you to select where to save the document and proposing a sanitized filename derived from the document's extracted title.
* **Default Directory (C:\\):** Preconfigured to open the save dialog at your system root `C:\` by default, with a seamless fallback to your User profile directory if root access is restricted.
* **Notepad++ Integration:** Automatically opens the generated markdown document in **Notepad++** immediately upon saving so you can review or edit it instantly.
* **Invisible Background Execution:** The server runs silently as a background service via `pythonw.exe` upon system startup, avoiding any intrusive command prompt windows on your desktop.

---

## 🛠️ Prerequisites

Before installing, please ensure your Windows environment matches the following prerequisites:

1. **Python 3.x installed** and added to your system `PATH` (make sure to check the *"Add Python to PATH"* checkbox during Python installation).
2. **Notepad++ installed** in its default location (`C:\Program Files\Notepad++\notepad++.exe` or `C:\Program Files (x86)\Notepad++\notepad++.exe`).
3. **Microsoft Print to PDF** enabled in Windows Optional Features (enabled by default on Windows 10 & 11).

---

## 📦 One-Click Installation

1. Download or clone this repository to a permanent directory on your computer (e.g., `C:\md_printer`).
2. Right-click **`install.bat`** and choose **"Run as Administrator"**.
3. The installer will automatically:
   * Verify your Python installation.
   * Install and upgrade all required Python dependencies (`pymupdf`, `pymupdf4llm`).
   * Add the local TCP/IP printer port at `127.0.0.1:9100`.
   * Create the **"Markdown Printer"** virtual printer queue.
   * Configure a silent background startup shortcut inside your Windows Startup folder.
   * Spin up the background print server immediately so it's ready to use.

---

## 📖 How to Use

Using Markdown Printer is incredibly simple:

1. Open any document you wish to convert (a PDF, a Word document, a webpage in your browser, an Excel spreadsheet, etc.).
2. Press `Ctrl + P` (or go to File > Print) and select **`Markdown Printer`** from your printer list.
3. Click **Print**.
4. Within seconds, a native Save File dialog will appear in the foreground, starting at `C:\` and proposing a clean filename.
5. Click **Save**. The conversion will run, images will be saved, and the file will **instantly open in Notepad++**!

---

## 📝 Event Logs

If you ever need to inspect the status of the print server, debug an issue, or track converted documents, the server maintains detailed, timestamped records in your user directory:

📁 Log File Location: `C:\Users\<Your-Username>\.md_printer.log`
