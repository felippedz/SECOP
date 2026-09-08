from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def export_documents_excel(documents: list[dict[str, Any]], output_path: Path | str) -> None:
    df = pd.DataFrame(documents)
    columns = ["nombre", "accion", "obligatorio", "pagina", "evidencia", "confianza"]
    for column in columns:
        if column not in df.columns:
            df[column] = None
    df = df[columns]
    df.to_excel(output_path, index=False)


def export_items_excel(items: list[dict[str, Any]], output_path: Path | str) -> None:
    df = pd.DataFrame(items)
    columns = [
        "item",
        "descripcion",
        "unidad",
        "cantidad",
        "codigo_unspsc",
        "rubro",
        "categoria",
        "precio_referencia",
        "valor_unitario",
        "valor_total",
        "pagina",
        "confianza",
    ]
    for column in columns:
        if column not in df.columns:
            df[column] = None
    df = df[columns]
    df.to_excel(output_path, index=False)
