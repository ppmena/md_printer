import os
import sys
import re
import socket
import tempfile
import datetime
import logging
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# Configure Logging
log_file = os.path.join(os.path.expanduser("~"), ".md_printer.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

DEFAULT_DIR = "C:\\"
HOST = "127.0.0.1"
PORT = 9100

def get_fallback_dir():
    """Returns a valid default directory if the primary C:\\ folder doesn't exist."""
    if os.path.exists(DEFAULT_DIR):
        return DEFAULT_DIR

    # Fallback to user home directory if C:\\ cannot be accessed
    return os.path.expanduser("~")

def sanitize_filename(name):
    """Sanitizes the filename to remove invalid characters for Windows filesystems."""
    if not name:
        return ""
    # Remove characters that are invalid in Windows filenames
    sanitized = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', name)
    # Remove null bytes or control characters
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
    # Collapse multiple spaces or underscores
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()

def extract_pdf_title(pdf_path):
    """Tries to extract a title from PDF metadata or content."""
    try:
        import pymupdf
        doc = pymupdf.open(pdf_path)
        title = doc.metadata.get("title")
        if title and title.strip():
            return sanitize_filename(title)

        # Fallback: inspect the first page text for potential titles
        if len(doc) > 0:
            first_page_text = doc[0].get_text().splitlines()
            for line in first_page_text:
                cleaned_line = line.strip()
                if len(cleaned_line) > 3 and len(cleaned_line) < 100:
                    return sanitize_filename(cleaned_line)
    except Exception as e:
        logging.error(f"Error trying to extract title from PDF: {e}")
    return ""

def open_in_notepad_plus_plus(filepath):
    """Launches Notepad++ if available; otherwise falls back to system default."""
    possible_paths = [
        r"C:\Program Files\Notepad++\notepad++.exe",
        r"C:\Program Files (x86)\Notepad++\notepad++.exe",
    ]
    npp_path = None
    for path in possible_paths:
        if os.path.exists(path):
            npp_path = path
            break

    if npp_path:
        logging.info(f"Opening {filepath} in Notepad++")
        subprocess.Popen([npp_path, filepath])
    else:
        logging.info(f"Notepad++ not found. Falling back to default system tool for {filepath}")
        try:
            os.startfile(filepath)
        except Exception as e:
            logging.error(f"Failed to open file automatically: {e}")

def process_pdf(pdf_path):
    """Converts PDF to structured Markdown and saves images."""
    try:
        import pymupdf
        import pymupdf4llm
    except ImportError as e:
        msg = f"Missing Python dependencies to process PDF: {e}. Please run install.bat"
        logging.error(msg)
        show_error_dialog("Dependency Error", msg)
        return

    # 1. Propose default name
    proposed_title = extract_pdf_title(pdf_path)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    if proposed_title:
        default_filename = f"{proposed_title}_{timestamp}.md"
    else:
        default_filename = f"Document_{timestamp}.md"

    # 2. Tkinter prompt in foreground
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    root.focus_force()

    initial_dir = get_fallback_dir()
    logging.info(f"Prompting save file dialog. Initial dir: {initial_dir}, Default filename: {default_filename}")

    save_path = filedialog.asksaveasfilename(
        parent=root,
        title="Save Structured Document as Markdown",
        initialdir=initial_dir,
        initialfile=default_filename,
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
    )

    if not save_path:
        logging.info("User cancelled the save file dialog.")
        root.destroy()
        return

    root.destroy()

    # Normalize paths
    save_path = os.path.abspath(save_path)
    base_dir = os.path.dirname(save_path)
    filename_without_ext = os.path.splitext(os.path.basename(save_path))[0]

    # Create a dedicated directory per print job to organize markdown and parallel images cleanly
    doc_folder = os.path.join(base_dir, filename_without_ext)
    os.makedirs(doc_folder, exist_ok=True)

    final_md_path = os.path.join(doc_folder, f"{filename_without_ext}.md")
    images_folder_name = "images"
    images_absolute_folder = os.path.join(doc_folder, images_folder_name)
    os.makedirs(images_absolute_folder, exist_ok=True)

    logging.info(f"Creating doc folder: {doc_folder}")
    logging.info(f"Final Markdown path: {final_md_path}")
    logging.info(f"Images directory: {images_absolute_folder}")

    # 3. Perform conversion using pymupdf4llm
    try:
        # We temporarily change the current working directory to doc_folder
        # so that relative images paths inside Markdown work beautifully
        original_cwd = os.getcwd()
        os.chdir(doc_folder)

        logging.info("Starting PDF to Markdown conversion...")

        # VERY IMPORTANT: Disable the AI-layout module of PyMuPDF.
        # This prevents the layout module from segmenting the page into raw image chunks,
        # forcing the engine to extract pure text layer content as structured Markdown text,
        # while only extracting real embedded images or image-based information.
        pymupdf4llm.use_layout(False)

        md_text = pymupdf4llm.to_markdown(
            doc=pdf_path,
            write_images=True,
            image_path=images_folder_name,
            image_format="png",
            dpi=150,
            force_text=True
        )

        # Write Markdown file
        with open(final_md_path, "w", encoding="utf-8") as f:
            f.write(md_text)

        logging.info("Conversion completed successfully!")

        # Return to original CWD
        os.chdir(original_cwd)

        # Open in Notepad++
        open_in_notepad_plus_plus(final_md_path)

    except Exception as e:
        error_msg = f"Error during PDF to Markdown conversion: {e}"
        logging.error(error_msg, exc_info=True)
        show_error_dialog("Conversion Error", error_msg)

def show_error_dialog(title, message):
    """Displays an error dialog to the user."""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showerror(title, message, parent=root)
        root.destroy()
    except Exception as e:
        logging.error(f"Failed to show error dialog: {e}")

def run_server():
    """Starts the TCP/IP Print Server on port 9100."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow address reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
    except Exception as e:
        msg = f"Could not start print server on {HOST}:{PORT}. Maybe it's already running: {e}"
        logging.error(msg)
        show_error_dialog("Server Error", msg)
        sys.exit(1)

    server_socket.listen(5)
    logging.info(f"Markdown Printer Server listening on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = server_socket.accept()
            logging.info(f"Connection accepted from {addr}")

            # Temporary file to store the incoming print PDF stream
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
                temp_pdf_path = temp_pdf.name
                logging.info(f"Receiving print job stream into temporary file: {temp_pdf_path}")

                while True:
                    data = conn.recv(1024 * 1024)  # Read 1MB chunks
                    if not data:
                        break
                    temp_pdf.write(data)

            conn.close()
            logging.info(f"Finished receiving data. Total size: {os.path.getsize(temp_pdf_path)} bytes")

            # Process received PDF
            if os.path.getsize(temp_pdf_path) > 0:
                process_pdf(temp_pdf_path)
            else:
                logging.warning("Received empty print job.")

            # Clean up the temporary file
            try:
                os.remove(temp_pdf_path)
            except Exception as e:
                logging.warning(f"Could not remove temp file {temp_pdf_path}: {e}")

        except KeyboardInterrupt:
            logging.info("Server shutting down by user request.")
            break
        except Exception as e:
            logging.error(f"Error in server loop: {e}", exc_info=True)

def setup_windows_printer():
    """Runs PowerShell to set up the TCP/IP port, virtual printer, and startup shortcut via a clean dynamic script."""
    logging.info("Starting virtual printer configuration on Windows...")
    print(" - Configuring Windows TCP/IP Port, Printer Queue, and Startup shortcut...")

    script_dir = os.path.abspath(os.path.dirname(__file__))
    server_script_path = os.path.join(script_dir, "printer_server.py")

    # We use double curly braces {{ }} to prevent python f-string formatting errors on PowerShell braces
    ps_script = f"""
    $PortName = 'MarkdownPrinterPort'
    $PrinterName = 'Markdown Printer'
    $DriverName = 'Microsoft Print to PDF'

    Write-Host ' - Checking port...'
    $port = Get-PrinterPort -Name $PortName -ErrorAction SilentlyContinue
    if ($null -eq $port) {{
        Write-Host ' - Creating standard local TCP/IP Port on 127.0.0.1 (Port 9100)...'
        Add-PrinterPort -Name $PortName -PrinterHostAddress '127.0.0.1'
    }} else {{
        Write-Host ' - Port already exists.'
    }}

    Write-Host ' - Checking print driver...'
    $driver = Get-PrinterDriver -Name $DriverName -ErrorAction SilentlyContinue
    if ($null -eq $driver) {{
        Write-Error 'The Microsoft Print to PDF driver is not installed.'
        exit 1
    }}

    Write-Host ' - Checking printer queue...'
    $printer = Get-Printer -Name $PrinterName -ErrorAction SilentlyContinue
    if ($null -eq $printer) {{
        Write-Host ' - Creating virtual printer queue...'
        Add-Printer -Name $PrinterName -DriverName $DriverName -PortName $PortName
    }} else {{
        Write-Host ' - Printer already exists.'
    }}

    Write-Host ' - Setting up system startup shortcut...'
    $WshShell = New-Object -ComObject WScript.Shell
    $ShortcutPath = Join-Path $env:APPDATA 'Microsoft\\Windows\\Start Menu\\Programs\\Startup\\MarkdownPrinter.lnk'
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = 'pythonw.exe'
    $Shortcut.Arguments = '"{server_script_path}"'
    $Shortcut.WorkingDirectory = '{script_dir}'
    $Shortcut.WindowStyle = 7
    $Shortcut.Description = 'Markdown Printer Server'
    $Shortcut.Save()
    Write-Host ' - Startup shortcut configured successfully.'
    """

    # Write to a temporary ps1 file with UTF-8 BOM so Windows PowerShell processes non-ASCII characters and script cleanly
    with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="w", encoding="utf-8-sig") as f:
        f.write(ps_script)
        temp_path = f.name

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", temp_path],
            capture_output=True,
            text=True,
            encoding="cp850"
        )
        if result.returncode != 0:
            logging.error(f"PowerShell error during setup: {result.stderr}")
            print(f"[ERROR] Failed to configure printer on Windows:\n{result.stderr}")
            sys.exit(1)
        else:
            print(result.stdout)
            logging.info(result.stdout)
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_windows_printer()
    else:
        run_server()
