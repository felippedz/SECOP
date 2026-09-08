from __future__ import annotations

from typing import Any

import pdfplumber


def extract_tables_from_pdf(pdf_path: str, page_numbers: list[int] | None = None) -> list[dict[str, Any]]:
    """Intenta extraer tablas desde páginas de un PDF.

    El resultado se mantiene en formato estructurado para su análisis
    posterior por requisitos o ítems.
    """
    tables: list[dict[str, Any]] = []

    with pdfplumber.open(pdf_path) as pdf:
        pages_to_scan = pdf.pages if page_numbers is None else [pdf.pages[i] for i in page_numbers if i < len(pdf.pages)]
        for page_index, page in enumerate(pages_to_scan, start=1):
            extracted_tables = page.extract_tables()
            for table_index, table in enumerate(extracted_tables or []):
                clean_rows = []
                for row in table:
                    clean_rows.append([cell.strip() if cell is not None else "" for cell in row])
                tables.append(
                    {
                        "page": page_index,
                        "table_index": table_index,
                        "rows": clean_rows,
                    }
                )

    return tables
