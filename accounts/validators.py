import fitz  # PyMuPDF
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from docx import Document
import io


def validate_resume_size_and_type(file):
    """Validate resume file size, format, and integrity for PDF and DOCX files."""
    # 1. File Size Limit of 2MB
    limit = 2 * 1024 * 1024
    if file.size > limit:
        raise ValidationError("File too large. Resumes must be under 2MB.")

    # 2. Format & Integrity Check
    file_name = file.name.lower()
    
    if file_name.endswith('.pdf'):
        try:
            # Check if it's a valid PDF
            doc = fitz.open(stream=file.read(), filetype="pdf")
            if doc.page_count < 1:
                raise ValidationError("The PDF is empty.")
            doc.close()
        except Exception:
            raise ValidationError("The uploaded PDF is corrupt or invalid.")
        finally:
            file.seek(0) # Always reset the pointer

    elif file_name.endswith('.docx'):
        try:
            # Check if it's a valid Word Doc
            docx_bytes = io.BytesIO(file.read())
            doc = Document(docx_bytes)
            # Ensure there is at least some text content
            full_text = [para.text for para in doc.paragraphs]
            if not any(text.strip() for text in full_text):
                 raise ValidationError("The Word document appears to be empty.")
        except Exception:
            raise ValidationError("The uploaded .docx file is corrupt or invalid.")
        finally:
            file.seek(0)

    else:
        raise ValidationError("Unsupported file type. Please upload a PDF or DOCX.")