from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class RequirementEvidence(BaseModel):
    nombre: str
    accion: Literal["DILIGENCIAR", "PRESENTAR", "DILIGENCIAR Y PRESENTAR", "INFORMACIÓN"]
    obligatorio: bool = True
    pagina: int | None = None
    evidencia: str | None = None
    confianza: float = 0.0


class ItemEvidence(BaseModel):
    item: int | None = None
    descripcion: str | None = None
    unidad: str | None = None
    cantidad: float | int | None = None
    codigo_unspsc: str | None = None
    rubro: str | None = None
    categoria: str | None = None
    precio_referencia: float | int | None = None
    otros_precios: list[float | int] | None = None
    pagina: int | None = None
    confianza: float = 0.0


class RequirementGroup(BaseModel):
    nombre: str
    contenido: str | None = None
    pagina: int | None = None
    evidencia: str | None = None


class AIAnalysisResult(BaseModel):
    documentos: list[RequirementEvidence] = Field(default_factory=list)
    requisitos: list[RequirementGroup] = Field(default_factory=list)
    items: list[ItemEvidence] = Field(default_factory=list)
