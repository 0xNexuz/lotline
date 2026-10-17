from __future__ import annotations

import json
import mimetypes
from dataclasses import fields
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .agent import LotLineAgent
from .memory_graph import MemoryGraphStore
from .models import AlertInput


def create_agent() -> LotLineAgent:
    graph = MemoryGraphStore()
    graph.seed_northstar()
    return LotLineAgent(graph)


AGENT = create_agent()
FRONTEND_ROOT = Path(__file__).resolve().parents[1] / "frontend"


class Handler(BaseHTTPRequestHandler):
    server_version = "LotLine/0.1"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length) or b"{}")

    def _frontend(self, path: str) -> bool:
        relative = "index.html" if path == "/" else path.lstrip("/")
        target = (FRONTEND_ROOT / relative).resolve()
        if not target.is_relative_to(FRONTEND_ROOT) or not target.is_file():
            return False
        body = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
        return True

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/" or path in {"/styles.css", "/app.js", "/favicon.svg", "/site.webmanifest"} or path.startswith("/assets/"):
            if self._frontend(path):
                return
        if path == "/health":
            self._json(200, {"status": "ok", "graph_runtime": AGENT.graph.runtime_status})
            return
        if path.startswith("/v1/cases/"):
            try:
                self._json(200, AGENT.inspect(path.rsplit("/", 1)[-1]))
            except KeyError as exc:
                self._json(404, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path == "/v1/alerts/analyze":
                body = self._body()
                allowed = {item.name for item in fields(AlertInput)}
                unknown = sorted(set(body) - allowed)
                if unknown:
                    raise ValueError(f"Unknown fields: {', '.join(unknown)}")
                self._json(201, AGENT.analyze(AlertInput(**body)))
                return
            if path.endswith("/approve") and path.startswith("/v1/cases/"):
                case_id = path.split("/")[-2]
                self._json(200, AGENT.approve(case_id, self._body()["operator_id"]))
                return
            if path.endswith("/execute") and path.startswith("/v1/cases/"):
                case_id = path.split("/")[-2]
                self._json(200, AGENT.execute(case_id))
                return
            self._json(404, {"error": "not found"})
        except (KeyError, TypeError, ValueError, PermissionError) as exc:
            self._json(400, {"error": str(exc)})

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("LotLine local demo listening on http://127.0.0.1:8765")
    print("Runtime: MOCKED graph adapter (not FalkorDB)")
    server.serve_forever()


if __name__ == "__main__":
    main()
