from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from drilling_report_parser.runtime_files import append_jsonl, atomic_write_json, prune_jsonl


class RuntimeFilesTests(unittest.TestCase):
    def test_atomic_write_json_replaces_content_and_cleans_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "config.json"
            atomic_write_json(path, {"version": 1})
            atomic_write_json(path, {"version": 2, "name": "配置"}, private=True)

            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"version": 2, "name": "配置"})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])

    def test_append_jsonl_rotates_before_writing_new_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            append_jsonl(path, {"event": "first"})
            append_jsonl(path, {"event": "second"}, max_bytes=1)

            rotated = path.with_suffix(path.suffix + ".1")
            self.assertEqual(json.loads(rotated.read_text(encoding="utf-8")), {"event": "first"})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"event": "second"})

    def test_prune_jsonl_drops_old_invalid_and_excess_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "debug.jsonl"
            rows = [
                {"time": "2026-07-01T12:00:00Z", "index": 0},
                {"time": "2026-07-11T12:00:00Z", "index": 1},
                {"time": "2026-07-12T12:00:00Z", "index": 2},
                {"time": "2026-07-13T12:00:00Z", "index": 3},
            ]
            path.write_text("not-json\n" + "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            path.with_suffix(path.suffix + ".1").write_text("stale rotation", encoding="utf-8")

            result = prune_jsonl(
                path,
                retention_days=7,
                max_entries=2,
                max_bytes=1024,
                now=datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc),
            )

            retained = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["index"] for row in retained], [2, 3])
            self.assertEqual(result["before"], 5)
            self.assertEqual(result["after"], 2)
            self.assertFalse(path.with_suffix(path.suffix + ".1").exists())


if __name__ == "__main__":
    unittest.main()
