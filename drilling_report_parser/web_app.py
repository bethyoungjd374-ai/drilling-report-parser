from __future__ import annotations

import argparse
import cgi
import html
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .parser import parse_excel_report, write_structured_workbook


PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>钻井日报 Excel 解析</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 40px; max-width: 880px; }
    h1 { font-size: 28px; margin-bottom: 8px; }
    .panel { border: 1px solid #d0d7de; border-radius: 8px; padding: 24px; }
    input[type=file] { display: block; margin: 16px 0; }
    button { background: #1f4e78; color: white; border: 0; border-radius: 6px; padding: 10px 16px; cursor: pointer; }
    .hint { color: #57606a; }
  </style>
</head>
<body>
  <h1>钻井日报 Excel 解析</h1>
  <p class="hint">上传同模板导出的 .xlsx/.xlsm 文件，系统会生成按数据类型分 sheet 的结构化 Excel。</p>
  <div class="panel">
    <form action="/parse" method="post" enctype="multipart/form-data">
      <input type="file" name="report" accept=".xlsx,.xlsm" required>
      <button type="submit">上传并解析</button>
    </form>
  </div>
</body>
</html>
"""


class UploadHandler(BaseHTTPRequestHandler):
    server_version = "DrillingReportParser/0.1"

    def do_GET(self) -> None:
        if self.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        self._send_html(PAGE)

    def do_POST(self) -> None:
        if self.path != "/parse":
            self.send_error(404)
            return
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": self.headers.get("Content-Type", "")},
            )
            upload = form["report"] if "report" in form else None
            if upload is None or not getattr(upload, "filename", ""):
                self._send_html("<p>没有收到 Excel 文件。</p>", status=400)
                return

            suffix = Path(upload.filename).suffix.lower()
            if suffix not in {".xlsx", ".xlsm"}:
                self._send_html("<p>只支持 .xlsx 或 .xlsm 文件。</p>", status=400)
                return

            safe_name = Path(upload.filename).stem
            with tempfile.TemporaryDirectory(prefix="drilling-report-") as tmp:
                input_path = Path(tmp) / f"input{suffix}"
                output_path = Path(tmp) / f"{safe_name}_structured.xlsx"
                input_path.write_bytes(upload.file.read())
                result = parse_excel_report(input_path)
                write_structured_workbook(result, output_path)
                data = output_path.read_bytes()

            download_name = f"{safe_name}_structured.xlsx"
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", f'attachment; filename="{html.escape(download_name)}"')
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:  # pragma: no cover - keeps local upload server useful.
            self._send_html(f"<h1>解析失败</h1><pre>{html.escape(str(exc))}</pre>", status=500)

    def log_message(self, fmt: str, *args) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def _send_html(self, body: str, status: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local upload page for drilling report Excel parsing.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), UploadHandler)
    print(f"Upload page: http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
