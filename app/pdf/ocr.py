from __future__ import annotations

from typing import Any


class OCRAdapter:
    """Adaptador de OCR preparado para una futura implementación.

    Por ahora representa la extensión natural del sistema para manejar
    páginas escaneadas.
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled

    def process_page(self, page_text: str, page_number: int) -> dict[str, Any]:
        if not self.enabled:
            return {
                "page_number": page_number,
                "status": "not_configured",
                "text": page_text,
            }

        return {
            "page_number": page_number,
            "status": "ocr_pending",
            "text": page_text,
        }
