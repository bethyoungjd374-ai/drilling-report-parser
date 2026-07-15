from __future__ import annotations

import unittest

from drilling_report_parser.completion_pdf_parser import _clean_operation_details
from drilling_report_parser.text_structure import (
    column_text,
    join_translated_parts,
    normalize_multiline,
    normalize_pdf_ocr_text,
    normalize_translation_paragraph,
    split_preserving_layout,
)


class TextStructureTest(unittest.TestCase):
    def test_pdf_ocr_normalizer_repairs_only_high_confidence_patterns(self) -> None:
        source = (
            'FILTRA1700 BBL; INGRESA10000 GAL; CASING 9 58/IN; '
            'BROCA 12.1/4"; ESTABILIZADOR 12 ¼"; DESDE 8, 668\' MD; '
            'PROFUNDIDAD 9.937\' MD; SERIE HEDRON1700.'
        )

        normalized = normalize_pdf_ocr_text(source)

        self.assertIn("FILTRA 1700 BBL", normalized)
        self.assertIn("INGRESA 10000 GAL", normalized)
        self.assertIn("CASING 9 5/8IN", normalized)
        self.assertIn('BROCA 12 1/4"', normalized)
        self.assertIn('ESTABILIZADOR 12 1/4"', normalized)
        self.assertIn("DESDE 8,668' MD", normalized)
        self.assertIn("PROFUNDIDAD 9.937' MD", normalized)
        self.assertIn("SERIE HEDRON1700", normalized)

    def test_pdf_ocr_normalizer_joins_cross_line_inch_fraction(self) -> None:
        self.assertEqual(normalize_pdf_ocr_text('BROCA DE 8\n1/2" PDC'), 'BROCA DE 8 1/2" PDC')
        self.assertEqual(normalize_pdf_ocr_text("TABLA 40.\n1/2 SIN UNIDAD"), "TABLA 40.\n1/2 SIN UNIDAD")

    def test_coordinate_column_applies_ocr_normalization(self) -> None:
        words = [
            {"text": "FILTRA1700", "x0": 10, "top": 10},
            {"text": "BBL", "x0": 80, "top": 10},
        ]

        self.assertEqual(column_text(words, 0, 120), "FILTRA 1700 BBL")

    def test_operation_details_preserve_lines_and_original_punctuation(self) -> None:
        source = (
            "CIA SERTECPET ARMA COMPLETACIÓN COMO SIGUE:\n"
            "- BULL PLUG 3 1/2\" EUE BOX.\n"
            "- 2 EA TBG 3 1/2\" EUE BOX X PIN (PROVISTO POR PEC)\n"
            "REALIZA PRUEBA DE PRESIÓN CON 3000 PSI x 10 MIN, OK"
        )

        cleaned = _clean_operation_details(source)

        self.assertEqual(cleaned.count("\n"), 3)
        self.assertIn("(PROVISTO POR PEC)\n", cleaned)
        self.assertNotIn("(PROVISTO POR PEC);", cleaned)
        self.assertTrue(cleaned.endswith("OK"))

    def test_layout_split_and_join_restore_original_separators(self) -> None:
        source = "INTRO:\n- FIRST ITEM.\n- SECOND ITEM.\n\nFINAL OPERATION."
        parts = split_preserving_layout(source, max_chars=24)
        translated = [part.text.replace("INTRO", "引导").replace("ITEM", "项目").replace("FINAL OPERATION", "最终操作") for part in parts]

        result = join_translated_parts(parts, translated)

        self.assertEqual(result.count("\n"), source.count("\n"))
        self.assertIn("\n\n最终操作.", result)

    def test_translation_paragraph_flattens_visual_lines(self) -> None:
        source = "INTRO:\n- FIRST ITEM.\n- SECOND ITEM."

        self.assertEqual(normalize_translation_paragraph(source), "INTRO: - FIRST ITEM. - SECOND ITEM.")

    def test_multiline_normalizer_only_collapses_horizontal_spacing(self) -> None:
        value = "  INTRO:  \r\n\t- ITEM   ONE.\r\n\r\n FINAL  "

        self.assertEqual(normalize_multiline(value), "INTRO:\n- ITEM ONE.\n\nFINAL")


if __name__ == "__main__":
    unittest.main()
