from __future__ import annotations

import re
from typing import Any


def extract_requirements(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Extrae requisitos y documentos de un documento analizado.

    La heurística prioriza mostrar evidencia textual y página, en lugar de
    asumir que una palabra por sí sola vuelve obligatorio un requisito.
    """
    requirements: list[dict[str, Any]] = []
    pages = document.get("paginas", [])

    patterns = {
        "propuesta económica": "DILIGENCIAR",
        "registro único de proponentes": "PRESENTAR",
        "certificado de existencia y representación legal": "PRESENTAR",
        "hoja de vida": "PRESENTAR",
        "anexo técnico": "DILIGENCIAR Y PRESENTAR",
        "garantía": "PRESENTAR",
    }

    found_names: set[str] = set()
    for page in pages:
        page_text = page.get("text", "")
        page_number = page.get("page_number", 1)
        for name, accion in patterns.items():
            if name in page_text.lower() and name not in found_names:
                requirements.append(
                    {
                        "nombre": name.title(),
                        "accion": accion,
                        "obligatorio": True,
                        "pagina": page_number,
                        "evidencia": _extract_evidence(page_text, name),
                        "confianza": 0.8,
                    }
                )
                found_names.add(name)

    if not requirements:
        doc_text = "\n\n".join(page.get("text", "") for page in pages)
        requirements.append(
            {
                "nombre": "Documentos requeridos",
                "accion": "INFORMACIÓN",
                "obligatorio": False,
                "pagina": 1,
                "evidencia": doc_text[:250] if doc_text else "No encontrado",
                "confianza": 0.1,
            }
        )

    return requirements


def _extract_evidence(text: str, keyword: str) -> str:
    lower_text = text.lower()
    lower_keyword = keyword.lower()
    index = lower_text.find(lower_keyword)
    if index == -1:
        return "No encontrado"
    start = max(0, index - 120)
    end = min(len(text), index + len(keyword) + 180)
    return text[start:end].strip()
