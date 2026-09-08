from __future__ import annotations

import unicodedata
from typing import Any


def validate_results(
    requirements: list[dict[str, Any]],
    items: list[dict[str, Any]],
    document_text: str = "",
    exceptions: list[str] | None = None,
) -> dict[str, Any]:
    """Valida que los resultados extraídos sean consistentes."""
    issues: list[str] = []

    for requirement in requirements:
        if not requirement.get("nombre"):
            issues.append("Un documento no tiene nombre.")
        if not requirement.get("evidencia"):
            issues.append(f"Falta evidencia en: {requirement.get('nombre')}")
        if requirement.get("pagina") is not None and requirement.get("pagina") < 1:
            issues.append(f"Página inválida en: {requirement.get('nombre')}")

    for item in items:
        if not item.get("descripcion") or item.get("descripcion") == "No encontrado":
            issues.append(f"Descripción faltante en ítem: {item.get('item')}")
        if item.get("cantidad") is not None and not isinstance(item.get("cantidad"), (int, float)):
            issues.append(f"Cantidad inválida en ítem: {item.get('item')}")
        if item.get("pagina") is not None and item.get("pagina") < 1:
            issues.append(f"Página inválida en ítem: {item.get('item')}")

    duplicates = _detect_duplicate_items(items)
    if duplicates:
        issues.extend(duplicates)

    exception_check = evaluate_exceptions(document_text, exceptions or [])

    return {
        "valido": not issues,
        "issues": issues,
        "excepciones": exception_check,
        "viable": exception_check["viable"],
        "razones_no_viable": exception_check["razones_no_viable"],
    }


def evaluate_exceptions(document_text: str, exceptions: list[str]) -> dict[str, Any]:
    """Comprueba criterios suministrados por el usuario contra el PDF.

    La comprobación es deliberadamente conservadora: una excepción solo se
    considera cumplida si su texto, o sus términos relevantes, aparecen en el
    documento. El umbral contractual del MVP es 50%.
    """
    criteria = [exception.strip() for exception in exceptions if exception.strip()]
    normalized_text = _normalize(document_text)
    checks: list[dict[str, Any]] = []

    for criterion in criteria:
        normalized_criterion = _normalize(criterion)
        terms = [term for term in normalized_criterion.split() if len(term) >= 4]
        matched_terms = [term for term in terms if term in normalized_text]
        fulfilled = bool(normalized_criterion and normalized_criterion in normalized_text)
        if not fulfilled and terms:
            fulfilled = len(matched_terms) / len(terms) >= 0.5

        checks.append(
            {
                "criterio": criterion,
                "cumple": fulfilled,
                "evidencia": "Coincidencia encontrada en el PDF." if fulfilled else None,
                "razon": None if fulfilled else "No se encontró evidencia suficiente en el PDF.",
            }
        )

    total = len(checks)
    fulfilled_count = sum(1 for check in checks if check["cumple"])
    percentage = round((fulfilled_count / total) * 100, 2) if total else 100.0
    reasons = [
        f"{check['criterio']}: {check['razon']}"
        for check in checks
        if not check["cumple"]
    ]

    return {
        "criterios": checks,
        "total": total,
        "cumplidos": fulfilled_count,
        "porcentaje_cumplimiento": percentage,
        "umbral_minimo": 50.0,
        "viable": percentage >= 50.0,
        "razones_no_viable": reasons,
    }


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return " ".join(without_accents.lower().split())


def _detect_duplicate_items(items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in items:
        descriptor = item.get("descripcion") or ""
        if descriptor in seen:
            duplicates.append(f"Ítem duplicado: {descriptor[:80]}")
        seen.add(descriptor)
    return duplicates
