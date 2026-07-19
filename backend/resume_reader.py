import pdfplumber
from docx import Document

def extract_pdf_text(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_docx_text(docx_file):
    document = Document(docx_file)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text