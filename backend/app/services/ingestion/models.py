from dataclasses import dataclass


@dataclass
class ParsedPage:
    """
    Normalized unit of content produced by any ingestion parser.

    A page does not necessarily mean a physical PDF page.
    For TXT/DOCX/CSV/JSON/XLSX it represents a logical section.
    """

    page_number: int
    text: str