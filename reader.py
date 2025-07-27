import os
from PIL import Image, UnidentifiedImageError
import pytesseract

# Required for reading PDFs and DOCX
from PyPDF2 import PdfReader
from docx import Document

# ✅ Set the path to your installed Tesseract OCR binary
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ Define common image extensions
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]

def read_file_content(path):
    """
    Read file content based on file type.
    Silently skip unsupported or temporary/corrupt files.
    """
    try:
        # Skip temp/lock files like ~$Document.docx
        if os.path.basename(path).startswith("~$"):
            return None

        ext = os.path.splitext(path)[1].lower()

        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        elif ext == ".pdf":
            reader = PdfReader(path)
            return "\n".join([page.extract_text() or "" for page in reader.pages])

        elif ext == ".docx":
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif ext in IMAGE_EXTENSIONS:
            try:
                img = Image.open(path)
                text = pytesseract.image_to_string(img)
                return f"[Image: {os.path.basename(path)}]\n{text.strip()}"
            except UnidentifiedImageError:
                return None  # 🧩 Unsupported image format — skip

    except Exception:
        return None  # 🧩 Any unexpected error — silently skip

    return None  # 🧩 Unsupported file type — skip