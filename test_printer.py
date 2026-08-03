import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Insert current directory in PATH so we can import printer_server
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import printer_server

class TestMarkdownPrinter(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to work in
        self.test_dir = tempfile.mkdtemp()
        self.pdf_path = os.path.join(self.test_dir, "sample.pdf")

        # Generate a dynamic sample PDF using pymupdf
        import pymupdf
        doc = pymupdf.open()
        page = doc.new_page()
        # Insert a title line and paragraph text
        page.insert_text((50, 50), "Test Document Title", fontsize=16)
        page.insert_text((50, 100), "This is a test paragraph to verify that structured Markdown conversion works perfectly.")

        # Insert a real 1x1 pixel PNG image to test image extraction in non-layout mode
        tiny_png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
        rect = pymupdf.Rect(100, 150, 200, 250)
        page.insert_image(rect, stream=tiny_png_bytes)

        doc.save(self.pdf_path)
        doc.close()

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_sanitize_filename(self):
        bad_name = "my/file\\with:forbidden*characters?.md"
        good_name = printer_server.sanitize_filename(bad_name)
        self.assertNotIn("/", good_name)
        self.assertNotIn("\\", good_name)
        self.assertNotIn(":", good_name)
        self.assertNotIn("*", good_name)
        self.assertNotIn("?", good_name)
        self.assertEqual(good_name, "my_file_with_forbidden_characters_.md")

    def test_extract_pdf_title(self):
        title = printer_server.extract_pdf_title(self.pdf_path)
        # It should extract "Test Document Title" or similar from first line
        self.assertTrue(len(title) > 0)
        self.assertIn("Title", title)

    @patch("tkinter.Tk")
    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("printer_server.open_in_notepad_plus_plus")
    def test_process_pdf_conversion(self, mock_notepad, mock_asksaveas, mock_tk):
        # Mock Tk to prevent TclError in headless test environments
        mock_tk_instance = MagicMock()
        mock_tk.return_value = mock_tk_instance

        # Mock asksaveasfilename to return a path in our temporary folder
        target_md_name = "test_document_output.md"
        target_md_path = os.path.join(self.test_dir, target_md_name)
        mock_asksaveas.return_value = target_md_path

        # Run the process_pdf function
        printer_server.process_pdf(self.pdf_path)

        # The logic should have created a folder named after the markdown file
        expected_folder = os.path.join(self.test_dir, "test_document_output")
        self.assertTrue(os.path.exists(expected_folder), "Dedicated folder for printing should be created.")

        # And placed the markdown file inside it
        expected_md_file = os.path.join(expected_folder, "test_document_output.md")
        self.assertTrue(os.path.exists(expected_md_file), "Markdown file should exist inside the dedicated folder.")

        # And created an images subfolder "images" inside the dedicated folder
        expected_images_folder = os.path.join(expected_folder, "images")
        self.assertTrue(os.path.exists(expected_images_folder), "Images folder should exist inside the dedicated folder.")

        # Verify Markdown content
        with open(expected_md_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Test", content)
            self.assertIn("Document", content)

        # Verify that images actually got saved inside the images folder
        saved_images = os.listdir(expected_images_folder)
        self.assertTrue(len(saved_images) > 0, "At least one image should be saved inside the images folder.")
        for img in saved_images:
            self.assertTrue(img.endswith(".png"))

        # Verify that open_in_notepad_plus_plus was called with the final markdown file path
        mock_notepad.assert_called_once_with(expected_md_file)

if __name__ == "__main__":
    unittest.main()
