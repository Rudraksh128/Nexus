from pathlib import Path

from pypdf import PdfReader


def extract_pages(file_path: str | Path) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Returns:
        A list containing page number and extracted text.
    """

    reader = PdfReader(str(file_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text.strip(),
            }
        )

    return pages