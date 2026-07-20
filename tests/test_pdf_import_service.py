from __future__ import annotations

import pytest

from drilling_report_parser.pdf_import_service import pdf_import_strategy


@pytest.mark.parametrize("report_type", ["completion", "workover", "move"])
def test_each_pdf_category_has_an_independent_storage_strategy(report_type: str) -> None:
    strategy = pdf_import_strategy(report_type)

    assert strategy.import_type == report_type
    assert strategy.storage_report_type == report_type
    assert callable(strategy.parser)


def test_drilling_template_profiles_resolve_without_changing_storage_type() -> None:
    original = pdf_import_strategy("drilling", template_profile="original")
    compatible = pdf_import_strategy("drilling", template_profile="compatible")

    assert original.storage_report_type == compatible.storage_report_type == "drilling"
    assert original.template_profile == "original"
    assert compatible.template_profile == "compatible"
    assert original.parser is not compatible.parser


def test_unknown_pdf_category_is_rejected() -> None:
    with pytest.raises(ValueError, match="不支持的 PDF 日报类型"):
        pdf_import_strategy("unknown")
