import os
import shutil
import tempfile
import unittest
from pathlib import Path

import fitz

from app.main import analyze_pdf


class TestSECOPPipeline(unittest.TestCase):
    def test_analyze_pdf_generates_outputs(self):
        temp_dir = tempfile.mkdtemp(prefix="secop_test_")
        pdf_path = Path(temp_dir) / "sample.pdf"
        out_dir = Path(temp_dir) / "output"

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "PROCESO DE CONTRATACION\n")
        page.insert_text((72, 100), "Objeto del contrato: Compra de equipos de oficina.\n")
        page.insert_text((72, 130), "Propuesta económica. El oferente deberá diligenciar todas las casillas.\n")
        page.insert_text((72, 160), "RUP. El oferente debe presentar el registro único de proponentes.\n")
        page.insert_text((72, 190), "Item 1 - Silla ejecutiva. Cantidad 10 UND. Valor unitario $500000.\n")
        doc.save(pdf_path)
        doc.close()

        result = analyze_pdf(str(pdf_path), str(out_dir))

        self.assertIn("documentos", result)
        self.assertIn("items", result)
        self.assertTrue((out_dir / "documentos_a_presentar.xlsx").exists())
        self.assertTrue((out_dir / "items.xlsx").exists())
        self.assertTrue((out_dir / "documentos_a_presentar.json").exists())
        self.assertTrue((out_dir / "items.json").exists())
        self.assertTrue((out_dir / "resumen.txt").exists())

        shutil.rmtree(temp_dir)

    def test_exceptions_mark_process_not_viable_below_fifty_percent(self):
        temp_dir = tempfile.mkdtemp(prefix="secop_exceptions_")
        pdf_path = Path(temp_dir) / "exceptions.pdf"
        out_dir = Path(temp_dir) / "output"

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "El trabajo requiere taller físico.\n")
        doc.save(pdf_path)
        doc.close()

        result = analyze_pdf(
            str(pdf_path),
            str(out_dir),
            ["El trabajo requiere taller físico", "Debe entregar garantía de calidad", "Debe tener experiencia específica"],
        )

        exception_result = result["validacion"]["excepciones"]
        self.assertEqual(exception_result["cumplidos"], 1)
        self.assertEqual(exception_result["porcentaje_cumplimiento"], 33.33)
        self.assertFalse(exception_result["viable"])
        self.assertEqual(len(exception_result["razones_no_viable"]), 2)

        shutil.rmtree(temp_dir)

    def test_items_extracted_from_late_catalog_pages(self):
        temp_dir = tempfile.mkdtemp(prefix="secop_late_items_")
        pdf_path = Path(temp_dir) / "late_items.pdf"
        out_dir = Path(temp_dir) / "output"

        doc = fitz.open()

        for _ in range(601):
            doc.new_page()

        page602 = doc.new_page()
        page602.insert_text((72, 72), "LISTA DE BIENES Y SERVICIOS\n")
        page602.insert_text((72, 100), "ITEM 1 - Silla ejecutiva. Unidad: UND. Cantidad: 10. Valor unitario: $500000\n")
        page602.insert_text((72, 130), "ITEM 2 - Computador portatil. Unidad: UND. Cantidad: 15. Valor unitario: $1200000\n")

        doc.save(pdf_path)
        doc.close()

        result = analyze_pdf(str(pdf_path), str(out_dir))

        self.assertGreaterEqual(len(result["items"]), 2)
        self.assertEqual(result["item_start_page"], 602)
        self.assertIn("taller", result["lugar_principal_ejecucion"].lower())

        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
