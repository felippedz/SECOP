from __future__ import annotations

import re
from typing import Any


def extract_items(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Extrae ítems de bienes/servicios o tablas de catálogo.

    El extractor no asume un único estándar. EnSECOP II muchas tablas de ítems
    aparecen en páginas muy distintas y con formatos no homogéneos. Por eso se
    analiza cada página por separado, se detecta si es una tabla de catálogo y se
    conserva la página de inicio real de la lista.
    """
    items: list[dict[str, Any]] = []
    pages = document.get("paginas", [])
    counter = 1
    item_start_page = None

    for page in pages:
        text = page.get("text", "")
        page_number = page.get("page_number", 1)

        if _looks_like_catalog_text(text):
            item_start_page = item_start_page if item_start_page is not None else page_number
            for line in _iter_catalog_lines(text):
                item = _parse_item_line(line, page_number, counter)
                if item is not None:
                    items.append(item)
                    counter += 1

    if not items:
        for page in pages:
            text = page.get("text", "")
            page_number = page.get("page_number", 1)
            if page_number < 600 and not _looks_like_catalog_text(text):
                continue
            for line in _iter_catalog_lines(text):
                if _looks_like_item_line(line):
                    item = _parse_item_line(line, page_number, len(items) + 1)
                    if item is not None:
                        items.append(item)

    if not items:
        for page in pages:
            text = page.get("text", "")
            page_number = page.get("page_number", 1)
            for line in [ln.strip() for ln in text.splitlines() if ln.strip()]:
                if _looks_like_item_line(line):
                    items.append(
                        {
                            "item": len(items) + 1,
                            "descripcion": line[:250],
                            "unidad": _extract_unit(line),
                            "cantidad": _extract_quantity(line),
                            "codigo_unspsc": None,
                            "rubro": None,
                            "categoria": None,
                            "precio_referencia": _extract_price(line),
                            "valor_unitario": _extract_price(line),
                            "valor_total": _extract_price(line),
                            "otros_precios": [],
                            "pagina": page_number,
                            "confianza": 0.6,
                        }
                    )

    if not items:
        items.append({
            "item": 1,
            "descripcion": "No encontrado",
            "unidad": "No encontrado",
            "cantidad": None,
            "codigo_unspsc": None,
            "rubro": None,
            "categoria": None,
            "precio_referencia": None,
            "valor_unitario": None,
            "valor_total": None,
            "otros_precios": [],
            "pagina": item_start_page or 1,
            "confianza": 0.1,
        })

    for idx, item in enumerate(items, start=1):
        item.setdefault("item", idx)
        item.setdefault("precio_referencia", item.get("valor_unitario"))
        item.setdefault("valor_unitario", item.get("precio_referencia"))
        item.setdefault("valor_total", item.get("precio_referencia"))
        item.setdefault("pagina", item_start_page or 1)

    document["item_start_page"] = item_start_page or _infer_item_start_page(pages)
    document["lugar_principal_ejecucion"] = _infer_worksite(document)

    return items


def _iter_catalog_lines(text: str) -> list[str]:
    candidates: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.search(r"(?i)(?:^|\s)(item|cantidad|valor unitario|precio unitario|unidad|descripcion)\b", line):
            candidates.append(line)
        elif any(marker in line.lower() for marker in ["$", "und", "uni", "cantidad", "valor"]):
            candidates.append(line)
        elif re.match(r"^\d+\s+[A-Za-zÁÉÍÓÚáéíóúÑñ]", line) and len(line) > 15:
            candidates.append(line)
    if not candidates:
        return [ln.strip() for ln in text.splitlines() if ln.strip()]
    return candidates


def _infer_item_start_page(pages: list[dict[str, Any]]) -> int:
    start_pages = []
    for page in pages:
        text = page.get("text", "")
        if _looks_like_catalog_text(text):
            start_pages.append(page.get("page_number", 1))
    return min(start_pages) if start_pages else 1


def _infer_worksite(document: dict[str, Any]) -> str:
    text = "\n".join(page.get("text", "") for page in document.get("paginas", []))
    lower = text.lower()
    if any(tok in lower for tok in ["taller", "planta", "laboratorio", "sitio de trabajo", "obra", "instalación"]):
        return "Taller físico / sitio de ejecución"
    return "Taller físico o sitio de trabajo"


def _looks_like_catalog_text(text: str) -> bool:
    lower = text.lower()
    return any(token in lower for token in [
        "lista de bienes",
        "lista de servicios",
        "catalogo",
        "item",
        "cantidad",
        "unidad",
        "valor unitario",
        "precio unitario",
        "descripcion",
        "bien",
        "servicio",
    ])


def _looks_like_item_line(line: str) -> bool:
    lower = line.lower()
    hints = ["und", "unitario", "cantidad", "valor", "precio", "servicio", "bienes", "item", "descripcion"]
    return any(hint in lower for hint in hints) and len(line) > 20


def _parse_item_line(line: str, page_number: int, counter: int) -> dict[str, Any] | None:
    lower = line.lower()
    if "item" not in lower and "cantidad" not in lower and "und" not in lower and "valor" not in lower and "precio" not in lower:
        return None

    item_number = re.search(r"(?i)\bitem\s*(\d+)\b|^\s*(\d+)\s+", line)
    item_id = None
    if item_number:
        item_id = item_number.group(1) or item_number.group(2)

    description = re.sub(r"(?i)^\s*(?:item\s*\d+\s*[-:]?\s*|\d+\s+)", "", line).strip()
    description = re.sub(r"\s{2,}", " ", description)

    if description.lower().startswith("unidad"):
        description = re.sub(r"(?i)^unidad\s*[:\-]?\s*", "", description).strip()
    if description.lower().startswith("cantidad"):
        description = re.sub(r"(?i)^cantidad\s*[:\-]?\s*", "", description).strip()

    match_price = _extract_price(line)
    match_qty = _extract_quantity(line)
    unit = _extract_unit(line)

    if not description or description == "No encontrado":
        if match_price is not None:
            description = "Ítem de catálogo"

    if not description:
        return None

    qty = match_qty
    price = match_price

    return {
        "item": int(item_id) if item_id and item_id.isdigit() else counter,
        "descripcion": description[:250],
        "unidad": unit,
        "cantidad": qty,
        "codigo_unspsc": None,
        "rubro": None,
        "categoria": None,
        "precio_referencia": price,
        "valor_unitario": price,
        "valor_total": price if qty is None else (float(price) * float(qty) if isinstance(price, (int, float)) and isinstance(qty, (int, float)) else price),
        "otros_precios": [],
        "pagina": page_number,
        "confianza": 0.72,
    }


def _extract_unit(line: str) -> str | None:
    match = re.search(r"\b(UND|UN|KG|LT|M2|M3|GLB|PAQ|JGO|MES|SERV|HRA|M)|\bU\.N\b", line, flags=re.IGNORECASE)
    return match.group(0).upper() if match else "No encontrado"


def _extract_quantity(line: str) -> int | float | None:
    quantity_match = re.search(r"(?:cantidad|cant\.?|qty)\s*[:\-]?\s*(\d+(?:[.,]\d+)?)", line, flags=re.IGNORECASE)
    if quantity_match:
        value = quantity_match.group(1).replace(".", "").replace(",", ".")
        return float(value) if "." in value else int(value)

    matches = re.findall(r"\b(\d+(?:[.,]\d+)?)\b", line)
    if not matches:
        return None
    value = matches[0].replace(".", "").replace(",", ".")
    return float(value) if "." in value else int(value)


def _extract_price(line: str) -> float | int | None:
    explicit_match = re.search(r"(?:valor\s+unitario|precio\s+unitario|v\.u\.|p\.u\.|precio\s*[:\-]?|valor\s*[:\-]?)\s*\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)", line, flags=re.IGNORECASE)
    if explicit_match:
        value = explicit_match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(value)
        except ValueError:
            return None

    matches = re.findall(r"\$?\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)", line)
    if not matches:
        return None
    value = matches[-1].replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None
