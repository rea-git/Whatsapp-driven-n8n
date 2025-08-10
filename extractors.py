# flask_mvp/extractors.py
import io
from typing import Optional

# Minimal deps: pdfminer.six, python-docx
from pdfminer.high_level import extract_text as pdf_extract_text
import docx

def extract_text_from_file(raw_bytes: bytes, filename: str) -> str:
    fname = filename.lower()
    if fname.endswith('.pdf'):
        try:
            return pdf_extract_text(io.BytesIO(raw_bytes))
        except Exception as e:
            return f"[error extracting pdf: {e}]"
    elif fname.endswith('.docx'):
        try:
            doc = docx.Document(io.BytesIO(raw_bytes))
            return '\n'.join(p.text for p in doc.paragraphs)
        except Exception as e:
            return f"[error extracting docx: {e}]"
    elif fname.endswith('.txt'):
        try:
            return raw_bytes.decode('utf-8', errors='replace')
        except:
            return raw_bytes.decode('latin-1', errors='replace')
    else:
        # fallback: try PDF first otherwise return empty
        try:
            return pdf_extract_text(io.BytesIO(raw_bytes))
        except:
            return ''