# SECOP Analyzer

Aplicación Python para analizar procesos de contratación pública de SECOP II y extraer información relevante de un PDF.

## Objetivo

El sistema procesa un PDF grande de un proceso de contratación y genera resultados estructurados sobre:

- documentos que debe presentar el oferente,
- documentos o formularios que debe diligenciar,
- requisitos importantes,
- bienes o servicios solicitados,
- evidencia y páginas de origen.

## Estructura del proyecto

```text
secop_analyzer/
├── app/
│   ├── pdf/
│   │   ├── extractor.py
│   │   ├── tables.py
│   │   └── ocr.py
│   ├── ai/
│   │   ├── analyzer.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   ├── analysis/
│   │   ├── sections.py
│   │   ├── requirements.py
│   │   └── items.py
│   ├── exporters/
│   │   ├── excel.py
│   │   ├── json.py
│   │   └── pdf.py
│   ├── validators.py
│   └── main.py
├── data/
│   ├── input/
│   └── output/
├── tests/
├── requirements.txt
├── README.md
└── .env.example
```

## Flujo

1. Leer PDF
2. Extraer texto por página
3. Detectar tablas e ítems
4. Identificar secciones relevantes
5. Analizar fragmentos con IA
6. Validar datos
7. Generar JSON/Excel

## Uso rápido

```bash
python app/main.py --pdf data/input/proceso.pdf --output data/output
```

## Nota

Este MVP está diseñado para funcionar sin IA externa si no se configura una API, usando un motor de análisis local basado en reglas y heurísticas. La integración con IA se mantiene separada en `app/ai` para facilitar cambiar de proveedor.
