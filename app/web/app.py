from __future__ import annotations

import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

from app.main import analyze_pdf

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "data", "input")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download")
def download_file():
    file_path = request.args.get("file")
    if not file_path:
        return jsonify({"error": "No se indicó el archivo a descargar."}), 400

    target = Path(file_path)
    if not target.exists() or target.suffix.lower() != ".docx":
        return jsonify({"error": "Archivo no disponible para descarga."}), 404

    return send_file(target, as_attachment=True, download_name=target.name)


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No se recibió ningún archivo PDF."}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "Debe seleccionar un archivo PDF."}), 400

    if not uploaded_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "El archivo debe tener extensión .pdf."}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    temp_dir = tempfile.mkdtemp(prefix="secop_web_")
    pdf_path = Path(temp_dir) / uploaded_file.filename
    uploaded_file.save(pdf_path)

    exceptions_text = request.form.get("excepciones", "")
    exceptions = [line.strip() for line in exceptions_text.splitlines() if line.strip()]
    output_dir = Path(temp_dir) / "output"
    result = analyze_pdf(str(pdf_path), str(output_dir), exceptions)
    word_file = Path(result.get("word_file", output_dir / "documentos_y_requisitos.docx"))

    return jsonify(
        {
            "status": "ok",
            "pdf": uploaded_file.filename,
            "total_paginas": result.get("total_paginas"),
            "documentos": result.get("documentos", []),
            "items": result.get("items", []),
            "excepciones": result.get("validacion", {}).get("excepciones", {}),
            "item_start_page": result.get("item_start_page"),
            "lugar_principal_ejecucion": result.get("lugar_principal_ejecucion"),
            "validacion": result.get("validacion", {}),
            "output_dir": str(output_dir),
            "word_file": str(word_file),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
