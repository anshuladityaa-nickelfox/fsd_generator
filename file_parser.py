import fitz  # PyMuPDF
from docx import Document

def parse_docx(file):
    try:
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error parsing DOCX: {e}"

def parse_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        return f"Error parsing PDF: {e}"

def parse_file(uploaded_file):
    if uploaded_file.name.endswith('.docx'):
        return parse_docx(uploaded_file)
    elif uploaded_file.name.endswith('.pdf'):
        return parse_pdf(uploaded_file)
    else:
        # Fallback to plain text
        try:
            return uploaded_file.getvalue().decode('utf-8')
        except Exception as e:
            return f"Error parsing text file: {e}"
