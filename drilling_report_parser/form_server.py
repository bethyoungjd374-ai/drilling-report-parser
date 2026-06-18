from __future__ import annotations

import argparse
import cgi
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from .completion_pdf_parser import parse_completion_pdf_daily_report
from .move_pdf_parser import parse_move_pdf_daily_report
from .pdf_report_parser import parse_pdf_daily_report
from .workover_pdf_parser import parse_workover_pdf_daily_report


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web_form"


class FormHandler(BaseHTTPRequestHandler):
    server_version = "DrillingReportForm/0.1"

    def do_GET(self) -> None:
        if self.path in {"/", ""}:
            self.send_response(302)
            self.send_header("Location", "/web_form/")
            self.end_headers()
            return
        if self.path == "/web_form":
            self.send_response(302)
            self.send_header("Location", "/web_form/")
            self.end_headers()
            return
        self._serve_static()

    def do_POST(self) -> None:
        if self.path == "/api/import-pdf":
            self._import_pdf()
            return
        if self.path == "/api/import-completion-pdf":
            self._import_completion_pdf()
            return
        if self.path == "/api/import-workover-pdf":
            self._import_workover_pdf()
            return
        if self.path == "/api/import-move-pdf":
            self._import_move_pdf()
            return
        self.send_error(404)

    def _import_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_completion_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_completion_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_workover_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_workover_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _import_move_pdf(self) -> None:
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_json({"error": "No PDF file received."}, status=400)
                return
            if Path(upload.filename).suffix.lower() != ".pdf":
                self._send_json({"error": "Only PDF files are supported."}, status=400)
                return
            payload = parse_move_pdf_daily_report(upload.file.read())
            payload.setdefault("metadata", {})["source_file"] = Path(upload.filename).name
            self._send_json(payload)
        except Exception as exc:  # pragma: no cover - keeps the local app useful.
            self._send_json({"error": str(exc)}, status=500)

    def _send_json(self, payload: dict[str, object], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _serve_static(self) -> None:
        raw_path = unquote(self.path.split("?", 1)[0])
        if raw_path.startswith("/web_form/"):
            rel = raw_path.removeprefix("/web_form/")
            target = WEB_ROOT / (rel or "index.html")
        else:
            self.send_error(404)
            return

        target = target.resolve()
        if not str(target).startswith(str(WEB_ROOT.resolve())) or not target.exists() or target.is_dir():
            self.send_error(404)
            return

        data = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if target.suffix in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the drilling report web form with PDF import.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FormHandler)
    print(f"Drilling report form: http://{args.host}:{args.port}/web_form/")
    server.serve_forever()


if __name__ == "__main__":
    main()
