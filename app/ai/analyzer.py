from __future__ import annotations

import json
from typing import Any

from app.ai.prompts import SECTION_PROMPT
from app.ai.schemas import AIAnalysisResult


class AIProvider:
    """Proveedor de IA con interfaz adaptable.

    En este MVP se usa un analizador local basado en reglas y JSON
    estructurado. La integración con un proveedor externo queda separada
    y lista para cambiar de implementación sin tocar el resto del flujo.
    """

    def analyze(self, text: str, page_number: int | None = None) -> AIAnalysisResult:
        text_clean = (text or "")[:5000]
        docs = self._heuristic_document_detection(text_clean)
        reqs = self._heuristic_requirements(text_clean)
        items = self._heuristic_items(text_clean)

        return AIAnalysisResult(
            documentos=docs,
            requisitos=reqs,
            items=items,
        )

    def _heuristic_document_detection(self, text: str) -> list[dict[str, Any]]:
        detected: list[dict[str, Any]] = []
        lower = text.lower()

        doc_patterns = {
            "propuesta económica": ("propuesta económica", "diligenciar"),
            "rúp": ("registro único de proponentes", "rup", "presentar"),
            "certificado de existencia y representación legal": ("certificado de existencia y representación legal", "presentar"),
            "hoja de vida": ("hoja de vida", "presentar"),
        }

        for name, (pattern1, pattern2) in doc_patterns.items():
            if pattern1 in lower or pattern2 in lower:
                detected.append(
                    {
                        "nombre": name.title(),
                        "accion": "DILIGENCIAR" if "diligenciar" in lower else "PRESENTAR",
                        "obligatorio": True,
                        "pagina": 1,
                        "evidencia": text[:250],
                        "confianza": 0.8,
                    }
                )

        if not detected:
            detected.append(
                {
                    "nombre": "Documentos requeridos",
                    "accion": "INFORMACIÓN",
                    "obligatorio": False,
                    "pagina": 1,
                    "evidencia": text[:250],
                    "confianza": 0.5,
                }
            )

        return detected

    def _heuristic_requirements(self, text: str) -> list[dict[str, Any]]:
        segments = []
        keywords = [
            "objeto del contrato",
            "alcance",
            "presupuesto",
            "cronograma",
            "requisitos para participar",
            "requisitos jurídicos",
            "requisitos financieros",
            "experiencia",
            "requisitos técnicos",
            "propuesta económica",
            "garantías",
            "factores de evaluación",
            "anexos",
            "obligaciones del contratista",
        ]

        for keyword in keywords:
            if keyword in text.lower():
                segments.append(
                    {
                        "nombre": keyword.title(),
                        "contenido": text[:500],
                        "pagina": 1,
                        "evidencia": text[:180],
                    }
                )

        return segments

    def _heuristic_items(self, text: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            if any(token in line.lower() for token in ["und", "unitario", "cantidad", "valor unitario"]):
                items.append(
                    {
                        "item": idx + 1,
                        "descripcion": line[:180],
                        "unidad": "No encontrado",
                        "cantidad": 1,
                        "codigo_unspsc": None,
                        "rubro": None,
                        "categoria": None,
                        "precio_referencia": None,
                        "otros_precios": [],
                        "pagina": 1,
                        "confianza": 0.65,
                    }
                )
        if not items:
            items.append(
                {
                    "item": 1,
                    "descripcion": "No encontrado",
                    "unidad": "No encontrado",
                    "cantidad": None,
                    "codigo_unspsc": None,
                    "rubro": None,
                    "categoria": None,
                    "precio_referencia": None,
                    "otros_precios": [],
                    "pagina": 1,
                    "confianza": 0.1,
                }
            )
        return items
