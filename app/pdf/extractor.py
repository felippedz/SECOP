from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import fitz


@dataclass
class PageData:
    page_number: int
    text: str = ""
    tables: list[dict[str, Any]] = field(default_factory=list)


def extract_pdf_text(pdf_path: Path) -> dict[str, Any]:
    """Extrae texto y metadata de un PDF usando PyMuPDF.

    Producción: el documento se guarda como una estructura con páginas,
    texto, contenido bruto y número total de páginas. También se deja
    lista la extracción de tablas para que módulos posteriores puedan
    inspeccionarla.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo PDF: {pdf_path}")

    doc = fitz.open(pdf_path)
    pages: list[PageData] = []

    for page_index in range(doc.page_count):
        page = doc[page_index]
        text = page.get_text("text")
        pages.append(
            PageData(
                page_number=page_index + 1,
                text=text or "",
                tables=[],
            )
        )

    doc.close()

    return {
        "pdf_path": str(pdf_path),
        "total_paginas": len(pages),
        "paginas": [
            {
                "page_number": page.page_number,
                "text": page.text,
                "tables": page.tables,
            }
            for page in pages
        ],
        "texto_completo": "\n\n".join(page["text"] for page in [
            {
                "page_number": page.page_number,
                "text": page.text,
                "tables": page.tables,
            }
            for page in pages
        ]),
    }
