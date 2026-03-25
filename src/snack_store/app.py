from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from .catalog import list_snacks


class SnackHandler(BaseHTTPRequestHandler):
    def _json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path == "/api/snacks":
            self._json(200, {"items": list_snacks()})
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/api/orders":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length or 0)
            body = json.loads(raw.decode("utf-8") or "{}") if raw else {}
            self._json(201, {"message": "order_created", "payload": body})
            return
        self._json(404, {"error": "not_found"})


def main():
    server = HTTPServer(("127.0.0.1", 8000), SnackHandler)
    print("Snack API running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
