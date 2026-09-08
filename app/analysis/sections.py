from __future__ import annotations

from typing import Any


SECTION_KEYWORDS = {
    "información general": ["información general", "identificación del proceso", "datos del proceso"],
    "objeto del contrato": ["objeto del contrato", "objeto social", "objeto del proceso"],
    "alcance": ["alcance", "alcance del contrato"],
    "presupuesto": ["presupuesto", "valor estimado", "valor total"],
    "cronograma": ["cronograma", "plazo", "fecha de cierre", "fecha de inicio"],
    "requisitos para participar": ["requisitos para participar", "participación"],
    "requisitos jurídicos": ["requisitos jurídicos", "personería jurídica", "representación legal"],
    "requisitos financieros": ["requisitos financieros", "capacidad financiera"],
    "experiencia": ["experiencia", "experiencia mínima"],
    "requisitos técnicos": ["requisitos técnicos", "capacidad técnica"],
    "propuesta económica": ["propuesta económica"],
    "garantías": ["garantías", "seguro de buena ejecución"],
    "factores de evaluación": ["factores de evaluación", "criterios de evaluación"],
    "anexos": ["anexos", "anexo"],
    "lista de bienes o servicios": ["lista de bienes", "lista de servicios", "catalogo", "ítems"],
    "obligaciones del contratista": ["obligaciones del contratista", "deberes del contratista"],
    "otra información relevante": ["otra información relevante", "información adicional"],
}


def detect_sections(text: str) -> dict[str, Any]:
    """Identifica secciones relevantes en el texto del PDF.

    En lugar de buscar palabras aisladas, se usa un conjunto de patrones
    por sección y el contexto del documento. Esto facilita detectar la
    función de cada bloque textual.
    """
    lower = text.lower()
    hits: dict[str, Any] = {}

    for section, patterns in SECTION_KEYWORDS.items():
        matches = [pattern for pattern in patterns if pattern in lower]
        if matches:
            hits[section] = {
                "pagina": 1,
                "evidencia": next((pattern for pattern in matches), ""),
                "contexto": text[:300],
            }

    return hits
