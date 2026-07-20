from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from drilling_report_parser.mysql_database import _connect, initialize_database  # noqa: E402


DEFAULT_OUTPUT_DIR = ROOT / "outputs" / f"data-acceptance-{date.today().isoformat()}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit normalized daily-report data and the official statistics readiness gate."
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        help="Optional root containing source PDFs. Basenames are matched Unicode-insensitively.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--skip-initialize", action="store_true")
    args = parser.parse_args()

    if not args.skip_initialize:
        initialize_database()
    snapshot = collect_acceptance_snapshot(source_root=args.source_root)
    paths = write_snapshot(snapshot, args.output_dir)
    print(json.dumps({"summary": snapshot["summary"], "outputs": paths}, ensure_ascii=False, indent=2))
    return 0 if snapshot["summary"]["technical_acceptance_status"] == "PASS" else 1


def collect_acceptance_snapshot(*, source_root: Path | None = None) -> dict[str, Any]:
    with _connect() as connection:
        with connection.cursor() as cursor:
            records = _fetch_all(
                cursor,
                """
                SELECT source.record_id,source.report_type,source.report_date,source.report_no,
                       source.rig,source.wellbore,source.source_file,source.source_page_start,
                       source.source_page_end,source.validation_status,source.validation_warnings,
                       source.master_match_status,source.translation_status,source.translation_progress,
                       report.normalization_status
                FROM dpr_report_record source
                LEFT JOIN dpr_report report ON report.record_id=source.record_id
                ORDER BY source.report_date,source.record_id
                """,
            )
            operation_rows = _fetch_all(
                cursor,
                """
                SELECT record_id,COUNT(*) AS operation_count,
                       ROUND(SUM(declared_hours),3) AS parsed_hours,
                       SUM(time_validation_status<>'VALID') AS invalid_time_rows,
                       SUM(started_at IS NULL OR ended_at IS NULL OR declared_hours IS NULL
                           OR work_category_code='' OR work_subcategory_code=''
                           OR operation_details_normalized='') AS missing_structured_rows,
                       SUM(statistics_status='READY') AS ready_rows,
                       SUM(statistics_status<>'READY') AS pending_rows,
                       ROUND(SUM(CASE WHEN statistics_status='READY' THEN statistical_hours ELSE 0 END),3)
                           AS ready_hours,
                       ROUND(SUM(CASE WHEN statistics_status<>'READY' THEN declared_hours ELSE 0 END),3)
                           AS pending_hours,
                       SUM(hours_source='CLOCK_DERIVED') AS clock_derived_rows
                FROM vw_operation_structured
                GROUP BY record_id
                """,
            )
            translation_rows = _fetch_all(
                cursor,
                "SELECT record_id,COUNT(*) AS translation_rows FROM translation_content GROUP BY record_id",
            )
            issue_rows = _fetch_all(
                cursor,
                """
                SELECT record_id,issue_type,severity,status
                FROM dq_issue
                WHERE status<>'RESOLVED'
                ORDER BY record_id,issue_type
                """,
            )
            by_type = _fetch_all(
                cursor,
                """
                SELECT report_type,COUNT(DISTINCT record_id) AS report_count,
                       COUNT(*) AS operation_count,ROUND(SUM(hours),3) AS parsed_hours,
                       ROUND(SUM(CASE WHEN statistics_status='READY' THEN statistical_hours ELSE 0 END),3)
                           AS official_hours,
                       ROUND(SUM(CASE WHEN statistics_status<>'READY' THEN hours ELSE 0 END),3)
                           AS pending_hours
                FROM vw_rig_production_timeline
                GROUP BY report_type
                ORDER BY report_type
                """,
            )
            invariants = _fetch_one(
                cursor,
                """
                SELECT
                  (SELECT COUNT(*) FROM dpr_report_record) AS report_records,
                  (SELECT COUNT(*) FROM dpr_report) AS normalized_reports,
                  (SELECT COUNT(*) FROM dpr_report_summary) AS summaries,
                  (SELECT COUNT(*) FROM dpr_operation) AS operations,
                  (SELECT COUNT(*) FROM dpr_operation_classification) AS classifications,
                  (SELECT COUNT(*) FROM vw_operation_structured) AS structured_view_rows,
                  (SELECT COUNT(*) FROM vw_rig_production_timeline) AS timeline_view_rows,
                  (SELECT COUNT(*) FROM dpr_report_record source
                    LEFT JOIN dpr_report report ON report.record_id=source.record_id
                    WHERE report.id IS NULL) AS reports_without_fact,
                  (SELECT COUNT(*) FROM dpr_report report
                    LEFT JOIN dpr_report_record source ON source.record_id=report.record_id
                    WHERE source.record_id IS NULL) AS orphan_report_facts,
                  (SELECT COUNT(*) FROM dpr_operation operation_row
                    LEFT JOIN dpr_report report ON report.id=operation_row.daily_report_id
                    WHERE report.id IS NULL) AS orphan_operations,
                  (SELECT COUNT(*) FROM dpr_operation_classification classification
                    LEFT JOIN dpr_operation operation_row ON operation_row.id=classification.activity_id
                    WHERE operation_row.id IS NULL) AS orphan_classifications,
                  (SELECT COUNT(*) FROM (
                    SELECT daily_report_id,source_row_no,COUNT(*) AS row_count
                    FROM dpr_operation GROUP BY daily_report_id,source_row_no HAVING COUNT(*)>1
                  ) duplicate_operation) AS duplicate_operation_keys,
                  (SELECT COUNT(*) FROM dq_issue
                    WHERE status<>'RESOLVED' AND severity='error') AS open_error_issues,
                  (SELECT COUNT(*) FROM dq_issue
                    WHERE status<>'RESOLVED' AND issue_type='RELATIONSHIP_OVERLAP') AS open_relationship_overlaps,
                  (SELECT COUNT(*) FROM dq_issue
                    WHERE status<>'RESOLVED' AND issue_type='CLASSIFICATION_PENDING')
                    AS open_classification_pending_issues,
                  (SELECT COUNT(DISTINCT record_id) FROM vw_operation_structured
                    WHERE statistics_status<>'READY') AS actual_pending_classification_reports,
                  (SELECT COUNT(*) FROM dq_issue issue
                    WHERE issue.status<>'RESOLVED' AND issue.issue_type='CLASSIFICATION_PENDING'
                      AND NOT EXISTS (
                        SELECT 1 FROM vw_operation_structured operation_row
                        WHERE operation_row.record_id=issue.record_id
                          AND operation_row.statistics_status<>'READY'
                      )) AS stale_classification_pending_issues,
                  (SELECT COUNT(*) FROM dpr_report_record source
                    LEFT JOIN translation_content content ON content.record_id=source.record_id
                    WHERE source.translation_status='COMPLETED'
                    GROUP BY source.record_id HAVING COUNT(content.record_id)=0 LIMIT 1)
                    AS completed_translation_without_rows
                """,
            )

    operation_by_record = {str(row["record_id"]): row for row in operation_rows}
    translation_by_record = {str(row["record_id"]): int(row.get("translation_rows", 0) or 0) for row in translation_rows}
    issues_by_record: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issue_rows:
        issues_by_record[str(issue.get("record_id", "") or "")].append(issue)

    source_index = _source_index(source_root) if source_root else None
    per_report: list[dict[str, Any]] = []
    for record in records:
        record_id = str(record.get("record_id", "") or "")
        operation = operation_by_record.get(record_id, {})
        source = _resolve_source(str(record.get("source_file", "") or ""), source_index)
        report_issues = issues_by_record.get(record_id, [])
        failed_codes: list[str] = []
        review_codes: list[str] = []
        if str(record.get("master_match_status", "") or "") != "MATCHED":
            failed_codes.append("MASTER_DATA_UNMATCHED")
        if str(record.get("normalization_status", "") or "") != "NORMALIZED":
            failed_codes.append("NORMALIZATION_INCOMPLETE")
        if int(operation.get("operation_count", 0) or 0) == 0:
            failed_codes.append("OPERATION_MISSING")
        if int(operation.get("invalid_time_rows", 0) or 0):
            failed_codes.append("OPERATION_TIME_INVALID")
        if int(operation.get("missing_structured_rows", 0) or 0):
            failed_codes.append("OPERATION_STRUCTURE_INCOMPLETE")
        if str(record.get("translation_status", "") or "") == "COMPLETED" and not translation_by_record.get(record_id):
            failed_codes.append("TRANSLATION_CONTENT_MISSING")
        if source["status"] in {"MISSING", "DIVERGENT_DUPLICATES"}:
            failed_codes.append(f"SOURCE_{source['status']}")
        if any(str(issue.get("severity", "") or "") == "error" for issue in report_issues):
            failed_codes.append("OPEN_DATA_QUALITY_ERROR")
        if int(operation.get("pending_rows", 0) or 0):
            review_codes.append("CLASSIFICATION_PENDING")
        parsed_hours = _number(operation.get("parsed_hours"))
        if abs(parsed_hours - 24.0) > 0.05:
            review_codes.append("BOUNDARY_HOURS_NOT_24")
        if any(str(issue.get("issue_type", "") or "") == "ALIAS_REVIEW" for issue in report_issues):
            review_codes.append("ALIAS_REVIEW")

        acceptance_status = "FAIL" if failed_codes else "REVIEW" if review_codes else "PASS"
        per_report.append(
            {
                "record_id": record_id,
                "report_type": str(record.get("report_type", "") or ""),
                "report_date": str(record.get("report_date", "") or ""),
                "rig": str(record.get("rig", "") or ""),
                "wellbore": str(record.get("wellbore", "") or ""),
                "source_file": str(record.get("source_file", "") or ""),
                "source_status": source["status"],
                "source_match_count": source["match_count"],
                "source_resolved_path": source["resolved_path"],
                "master_match_status": str(record.get("master_match_status", "") or ""),
                "normalization_status": str(record.get("normalization_status", "") or ""),
                "validation_status": str(record.get("validation_status", "") or ""),
                "translation_status": str(record.get("translation_status", "") or ""),
                "translation_rows": translation_by_record.get(record_id, 0),
                "operation_count": int(operation.get("operation_count", 0) or 0),
                "parsed_hours": parsed_hours,
                "ready_rows": int(operation.get("ready_rows", 0) or 0),
                "pending_rows": int(operation.get("pending_rows", 0) or 0),
                "official_hours": _number(operation.get("ready_hours")),
                "pending_hours": _number(operation.get("pending_hours")),
                "clock_derived_rows": int(operation.get("clock_derived_rows", 0) or 0),
                "open_issue_types": sorted({str(issue.get("issue_type", "") or "") for issue in report_issues}),
                "acceptance_status": acceptance_status,
                "issue_codes": sorted(set(failed_codes + review_codes)),
            }
        )

    parsed_hours_total = round(sum(_number(row.get("parsed_hours")) for row in by_type), 3)
    official_hours_total = round(sum(_number(row.get("official_hours")) for row in by_type), 3)
    pending_hours_total = round(sum(_number(row.get("pending_hours")) for row in by_type), 3)
    source_counts = Counter(row["source_status"] for row in per_report)
    status_counts = Counter(row["acceptance_status"] for row in per_report)

    checks = [
        _check("REPORT_FACT_1_TO_1", invariants["report_records"] == invariants["normalized_reports"], invariants),
        _check("REPORT_SUMMARY_1_TO_1", invariants["report_records"] == invariants["summaries"], invariants),
        _check("OPERATION_CLASSIFICATION_1_TO_1", invariants["operations"] == invariants["classifications"], invariants),
        _check("STRUCTURED_VIEW_ROW_RECONCILIATION", invariants["operations"] == invariants["structured_view_rows"], invariants),
        _check("TIMELINE_VIEW_ROW_RECONCILIATION", invariants["operations"] == invariants["timeline_view_rows"], invariants),
        _check(
            "NO_ORPHAN_OR_DUPLICATE_FACTS",
            not any(
                int(invariants.get(key, 0) or 0)
                for key in (
                    "reports_without_fact",
                    "orphan_report_facts",
                    "orphan_operations",
                    "orphan_classifications",
                    "duplicate_operation_keys",
                )
            ),
            invariants,
        ),
        _check("NO_OPEN_ERROR_ISSUES", int(invariants.get("open_error_issues", 0) or 0) == 0, invariants),
        _check(
            "NO_OPEN_RELATIONSHIP_OVERLAPS",
            int(invariants.get("open_relationship_overlaps", 0) or 0) == 0,
            invariants,
        ),
        _check(
            "NO_STALE_CLASSIFICATION_PENDING_ISSUES",
            int(invariants.get("stale_classification_pending_issues", 0) or 0) == 0,
            invariants,
        ),
        _check(
            "COMPLETED_TRANSLATIONS_HAVE_CONTENT",
            int(invariants.get("completed_translation_without_rows", 0) or 0) == 0,
            invariants,
        ),
        {
            "check_code": "SOURCE_PDF_PROVENANCE",
            "status": (
                "NOT_ASSESSED"
                if source_index is None
                else "PASS"
                if not source_counts.get("MISSING") and not source_counts.get("DIVERGENT_DUPLICATES")
                else "FAIL"
            ),
            "details": dict(source_counts),
        },
    ]
    technical_pass = not status_counts.get("FAIL") and all(
        check["status"] in {"PASS", "NOT_ASSESSED"} for check in checks
    )
    summary = {
        "generated_on": date.today().isoformat(),
        "technical_acceptance_status": "PASS" if technical_pass else "FAIL",
        "official_statistics_status": "PASS" if pending_hours_total == 0 else "REVIEW_REQUIRED",
        "business_universe_coverage_status": "NOT_ASSESSED",
        "report_count": int(invariants.get("report_records", 0) or 0),
        "operation_count": int(invariants.get("operations", 0) or 0),
        "parsed_hours": parsed_hours_total,
        "official_hours": official_hours_total,
        "pending_classification_hours": pending_hours_total,
        "statistics_readiness_percent": round(
            (official_hours_total / parsed_hours_total * 100) if parsed_hours_total else 0,
            1,
        ),
        "clock_derived_operation_rows": sum(int(row.get("clock_derived_rows", 0) or 0) for row in per_report),
        "report_acceptance_counts": dict(status_counts),
        "source_status_counts": dict(source_counts),
    }
    return {
        "summary": summary,
        "checks": checks,
        "by_report_type": [_json_safe(row) for row in by_type],
        "open_issue_counts": _issue_counts(issue_rows),
        "database_invariants": _json_safe(invariants),
        "reports": per_report,
    }


def write_snapshot(snapshot: dict[str, Any], output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "acceptance_snapshot.json"
    csv_path = output_dir / "report_acceptance.csv"
    json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    reports = list(snapshot.get("reports", []))
    fieldnames = list(reports[0]) if reports else []
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in reports:
            writer.writerow(
                {
                    key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
                    for key, value in row.items()
                }
            )
    return {"json": str(json_path.resolve()), "csv": str(csv_path.resolve())}


def _fetch_all(cursor: Any, sql: str, args: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cursor.execute(sql, args)
    return list(cursor.fetchall() or [])


def _fetch_one(cursor: Any, sql: str, args: tuple[Any, ...] = ()) -> dict[str, Any]:
    cursor.execute(sql, args)
    return dict(cursor.fetchone() or {})


def _source_index(source_root: Path) -> dict[str, list[Path]]:
    root = source_root.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Source root does not exist or is not a directory: {root}")
    index: dict[str, list[Path]] = defaultdict(list)
    for path in root.rglob("*"):
        if path.is_file():
            index[_normalized_name(path.name)].append(path)
    return index


def _resolve_source(source_file: str, source_index: dict[str, list[Path]] | None) -> dict[str, Any]:
    if source_index is None:
        return {"status": "NOT_ASSESSED", "match_count": 0, "resolved_path": ""}
    source_path = Path(source_file).expanduser()
    if source_path.is_absolute() and source_path.is_file():
        matches = [source_path.resolve()]
    else:
        matches = source_index.get(_normalized_name(source_path.name), [])
    if not matches:
        return {"status": "MISSING", "match_count": 0, "resolved_path": ""}
    if len(matches) == 1:
        return {"status": "RESOLVED", "match_count": 1, "resolved_path": str(matches[0].resolve())}
    hashes = {_sha256(path) for path in matches}
    status = "IDENTICAL_DUPLICATES" if len(hashes) == 1 else "DIVERGENT_DUPLICATES"
    return {
        "status": status,
        "match_count": len(matches),
        "resolved_path": str(sorted(matches, key=lambda value: str(value))[0].resolve()),
    }


def _normalized_name(value: str) -> str:
    return unicodedata.normalize("NFC", str(value or "")).casefold()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _number(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return round(float(value), 3)


def _check(code: str, passed: bool, details: dict[str, Any]) -> dict[str, Any]:
    return {"check_code": code, "status": "PASS" if passed else "FAIL", "details": _json_safe(details)}


def _issue_counts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(
        (str(row.get("issue_type", "") or ""), str(row.get("severity", "") or ""))
        for row in rows
    )
    return [
        {"issue_type": issue_type, "severity": severity, "count": count}
        for (issue_type, severity), count in sorted(counts.items())
    ]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
