import fitz

def extract_text(pdf_path: str) -> dict:
    doc = fitz.open(pdf_path)

    full_text = ""
    for page in doc:
        full_text += page.get_text()

    num_pages = doc.page_count
    doc.close()

    return {
        "full_text": full_text.strip(),
        "num_pages": num_pages,
        "char_count": len(full_text),
    }