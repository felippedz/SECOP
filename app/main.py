from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from app.analysis.requirements import extract_requirements
from app.analysis.items import extract_items
from app.exporters.excel import export_documents_excel, export_items_excel
from app.exporters.json import export_json
from app.exporters.word import export_requirements_word
from app.pdf.extractor import extract_pdf_text
from app.validators import validate_results


def analyze_pdf(
    pdf_path: str,
    output_dir: str = "data/output",
    exceptions: list[str] | None = None,
) -> dict:
    pdf_file = Path(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    document = extract_pdf_text(pdf_file)
    requirements = extract_requirements(document)
    items = extract_items(document)

    item_start_page = document.get("item_start_page", 1)
    lugar_principal = document.get("lugar_principal_ejecucion", "Taller físico o sitio de trabajo")

    validation = validate_results(
        requirements,
        items,
        document.get("texto_completo", ""),
        exceptions,
    )

    export_documents_excel(requirements, output_path / "documentos_a_presentar.xlsx")
    export_items_excel(items, output_path / "items.xlsx")
    export_json(requirements, output_path / "documentos_a_presentar.json")
    export_json(items, output_path / "items.json")
    word_path = output_path / "documentos_y_requisitos.docx"
    export_requirements_word(requirements, document, word_path)

    summary = {
        "pdf": str(pdf_file),
        "total_paginas": document["total_paginas"],
        "documentos": requirements,
        "items": items,
        "item_start_page": item_start_page,
        "lugar_principal_ejecucion": lugar_principal,
        "validacion": validation,
        "word_file": str(word_path),
    }

    (output_path / "resumen.txt").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Analiza un PDF de SECOP II")
    parser.add_argument("--pdf", required=True, help="Ruta al PDF de entrada")
    parser.add_argument("--output", default="data/output", help="Carpeta de salida")
    parser.add_argument(
        "--excepcion",
        action="append",
        default=[],
        help="Criterio de excepción a comprobar; puede repetirse.",
    )
    args = parser.parse_args()

    analyze_pdf(args.pdf, args.output, args.excepcion)
    print(f"Análisis completado. Resultado guardado en: {args.output}")


if __name__ == "__main__":
    main()
