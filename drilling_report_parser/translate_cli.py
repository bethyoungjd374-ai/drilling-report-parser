from __future__ import annotations

import argparse
import json
from pathlib import Path

from .parser import parse_excel_report
from .pdf_report_parser import parse_pdf_daily_report
from .translation import TranslationConfig, build_translator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Translate mixed Chinese/English/Spanish drilling daily report text with a local engine."
    )
    parser.add_argument("input", help="Path to .xlsx/.xlsm, .pdf, .json payload, or .txt source.")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the JSON translation result. Defaults to outputs/<input>_translation.json.",
    )
    parser.add_argument(
        "--engine",
        default=None,
        choices=["libretranslate", "noop"],
        help="Local translation engine adapter. Defaults to DRP_TRANSLATION_ENGINE or libretranslate.",
    )
    parser.add_argument(
        "--target-language",
        default=None,
        choices=["zh", "en", "es"],
        help="Target language. Defaults to DRP_TRANSLATION_TARGET or zh.",
    )
    parser.add_argument(
        "--libretranslate-url",
        default=None,
        help="Base URL for local LibreTranslate, for example http://127.0.0.1:5000.",
    )
    parser.add_argument(
        "--terms",
        default=None,
        help="Path to drilling_terms.json. Defaults to the package terminology file.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file does not exist: {input_path}")

    config = TranslationConfig.from_env()
    if args.engine:
        config = _replace_config(config, engine=args.engine)
    if args.target_language:
        config = _replace_config(config, target_language=args.target_language)
    if args.libretranslate_url:
        config = _replace_config(config, libretranslate_url=args.libretranslate_url.rstrip("/"))
    if args.terms:
        config = _replace_config(config, terms_path=Path(args.terms).expanduser().resolve())

    translator = build_translator(config)
    suffix = input_path.suffix.lower()
    if suffix in {".xlsx", ".xlsm"}:
        result = translator.translate_parse_result(parse_excel_report(input_path))
    elif suffix == ".pdf":
        result = translator.translate_report_payload(parse_pdf_daily_report(input_path))
    elif suffix == ".json":
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise SystemExit("JSON input must be an object payload.")
        result = translator.translate_report_payload(payload)
    else:
        result = translator.translate_plain_text(input_path.read_text(encoding="utf-8"))

    output_path = Path(args.output).expanduser().resolve() if args.output else _default_output(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Translation result: {output_path}")
    print(f"Engine: {result['metadata'].get('engine')}")
    print(f"Items: {result['metadata'].get('item_count')}")
    print(f"Translated: {result['metadata'].get('translated_count')}")
    warnings = result.get("warnings", [])
    if warnings:
        print(f"Warnings: {len(warnings)}")


def _replace_config(config: TranslationConfig, **updates: object) -> TranslationConfig:
    values = {
        "engine": config.engine,
        "target_language": config.target_language,
        "terms_path": config.terms_path,
        "libretranslate_url": config.libretranslate_url,
        "libretranslate_api_key": config.libretranslate_api_key,
        "timeout_seconds": config.timeout_seconds,
    }
    values.update(updates)
    return TranslationConfig(**values)


def _default_output(input_path: Path) -> Path:
    return Path.cwd() / "outputs" / f"{input_path.stem}_translation.json"


if __name__ == "__main__":
    main()
