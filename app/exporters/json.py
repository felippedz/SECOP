from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def export_json(data: list[dict[str, Any]] | dict[str, Any], output_path: Path | str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
