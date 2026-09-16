import io
import os
import fitz  # PyMuPDF
import docx  # python-docx
from app.config import settings
from app.core.exceptions import (
    DocumentParsingError,
    UnsupportedFileTypeError,
    EmptyDocumentError,
    FileTooLargeError
)

def validate_file_size(file_bytes: bytes):
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_size_bytes:
        raise FileTooLargeError(
            f"File size exceeds the limit of {settings.MAX_FILE_SIZE_MB}MB."
        )

def extract_text_from_pdf(file_bytes: bytes) -> str:
    validate_file_size(file_bytes)
    if not file_bytes:
        raise EmptyDocumentError()
    
    try:
        # Load PDF from memory stream
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentParsingError(f"Corrupted or invalid PDF file: {str(e)}")
        
    if doc.page_count == 0:
        raise EmptyDocumentError("The PDF document contains no pages.")
        
    text_content = []
    for page_num in range(doc.page_count):
        try:
            page = doc.load_page(page_num)
            text_content.append(page.get_text())
        except Exception as e:
            # Continue parsing other pages, but flag if all fail
            continue
            
    extracted_text = "\n".join(text_content).strip()
    if not extracted_text:
        raise EmptyDocumentError("No text could be extracted from the PDF file.")
        
    return extracted_text

def extract_text_from_docx(file_bytes: bytes) -> str:
    validate_file_size(file_bytes)
    if not file_bytes:
        raise EmptyDocumentError()
        
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise DocumentParsingError(f"Corrupted or invalid DOCX file: {str(e)}")
        
    text_content = []
    
    # Extract text from paragraphs
    for paragraph in doc.paragraphs:
        if paragraph.text:
            text_content.append(paragraph.text)
            
    # Extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_text = []
            for cell in row.cells:
                if cell.text:
                    row_text.append(cell.text.strip())
            if row_text:
                text_content.append(" | ".join(row_text))
                
    extracted_text = "\n".join(text_content).strip()
    if not extracted_text:
        raise EmptyDocumentError("No text could be extracted from the DOCX file.")
        
    return extracted_text

def extract_text_from_txt(file_bytes: bytes) -> str:
    validate_file_size(file_bytes)
    if not file_bytes:
        raise EmptyDocumentError()
        
    # Attempt decoding with utf-8, fallback to latin-1
    for encoding in ("utf-8", "latin-1", "utf-16"):
        try:
            extracted_text = file_bytes.decode(encoding).strip()
            if not extracted_text:
                raise EmptyDocumentError("The TXT file is empty.")
            return extracted_text
        except UnicodeDecodeError:
            continue
            
    raise DocumentParsingError("Failed to decode TXT file. Ensure it is a valid UTF-8, Latin-1, or UTF-16 text file.")

def extract_text(file_bytes: bytes, filename: str) -> str:
    if not filename:
        raise UnsupportedFileTypeError("Filename is missing.")
        
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        # Note: python-docx doesn't support old binary .doc, but we check .docx
        if ext == ".doc":
            raise UnsupportedFileTypeError("Older .doc format is not supported. Please convert to .docx.")
        return extract_text_from_docx(file_bytes)
    elif ext == ".txt":
        return extract_text_from_txt(file_bytes)
    else:
        raise UnsupportedFileTypeError(f"Unsupported file extension: {ext}. Only PDF, DOCX and TXT are supported.")
