import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


RECEIPT = os.environ.get("PRIVATE_RECEIPT", "NHNC{sample_receipt_goes_here}")
ALLOWED = {"http://127.0.0.1:8080", "http://localhost:8080"}


class Handler(BaseHTTPRequestHandler):
    server_version = "ArchiveHTTP/1.0"

    def log_message(self, fmt, *args):
        return

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path != "/archive/receipt":
            self.send_response(404)
            self.end_headers()
            return

        data = RECEIPT.encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _cors(self):
        origin = self.headers.get("Origin")
        if origin in ALLOWED:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 9100), Handler).serve_forever()
