"""FastAPI wrapper that runs the original form_server on an internal port
and proxies all incoming requests to it. This lets us keep the existing
BaseHTTPRequestHandler-based backend working under uvicorn/supervisor.
"""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Iterable

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

# Make the drilling_report_parser package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from http.server import ThreadingHTTPServer  # noqa: E402
from drilling_report_parser.form_server import FormHandler  # noqa: E402

INTERNAL_HOST = "127.0.0.1"
INTERNAL_PORT = int(os.environ.get("FORM_SERVER_PORT", "8090"))
UPSTREAM = f"http://{INTERNAL_HOST}:{INTERNAL_PORT}"

_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "transfer-encoding",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "upgrade",
    "content-encoding",
    "content-length",
    "host",
}


def _start_form_server() -> None:
    httpd = ThreadingHTTPServer((INTERNAL_HOST, INTERNAL_PORT), FormHandler)
    print(f"[form_server] listening on {INTERNAL_HOST}:{INTERNAL_PORT}")
    httpd.serve_forever()


_thread = threading.Thread(target=_start_form_server, daemon=True)
_thread.start()

# Wait until the internal server is ready (max ~5s)
for _ in range(50):
    try:
        with httpx.Client(timeout=0.3) as c:
            c.get(f"{UPSTREAM}/api/admin/session")
        break
    except Exception:
        time.sleep(0.1)

app = FastAPI(title="Drilling Report Parser Proxy")

_client = httpx.AsyncClient(base_url=UPSTREAM, timeout=60.0, follow_redirects=False)


def _filter_headers(headers: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    return [(k, v) for k, v in headers if k.lower() not in _HOP_BY_HOP]


@app.on_event("shutdown")
async def _shutdown() -> None:
    await _client.aclose()


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy(full_path: str, request: Request) -> Response:
    url = "/" + full_path
    if request.url.query:
        url = f"{url}?{request.url.query}"

    fwd_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }
    body = await request.body()

    upstream = await _client.request(
        request.method,
        url,
        headers=fwd_headers,
        content=body,
    )

    resp_headers = _filter_headers(upstream.headers.items())
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=dict(resp_headers),
        media_type=upstream.headers.get("content-type"),
    )
