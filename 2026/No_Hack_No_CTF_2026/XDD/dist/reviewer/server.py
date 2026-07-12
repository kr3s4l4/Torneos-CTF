import hashlib
import hmac
import html
import os
import secrets
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


HOST = "0.0.0.0"
PORT = 8081
SITE_PORT = int(os.environ.get("SITE_PORT", "8080"))
KEY = os.environ.get("REVIEW_KEY", secrets.token_hex(32)).encode()
DIFFICULTY = int(os.environ.get("STAMP_DIFFICULTY", "5"))
LIMIT = threading.Semaphore(2)
USED_TICKETS = {}
USED_LOCK = threading.Lock()


def make_ticket() -> str:
    ts = str(int(time.time()))
    nonce = secrets.token_hex(12)
    body = f"{ts}:{nonce}"
    mac = hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()
    return f"{body}:{mac}"


def check_ticket(ticket: str) -> bool:
    parts = ticket.split(":")
    if len(parts) != 3:
        return False
    ts, nonce, mac = parts
    if not ts.isdigit() or len(nonce) < 8:
        return False
    if abs(time.time() - int(ts)) > 600:
        return False
    body = f"{ts}:{nonce}"
    expected = hmac.new(KEY, body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, mac)


def check_stamp(ticket: str, stamp: str) -> bool:
    digest = hashlib.sha256(f"{ticket}:{stamp}".encode()).hexdigest()
    return digest.startswith("0" * DIFFICULTY)


def consume_ticket(ticket: str) -> bool:
    now = time.time()
    with USED_LOCK:
        expired = [key for key, expiry in USED_TICKETS.items() if expiry < now]
        for key in expired:
            del USED_TICKETS[key]
        if ticket in USED_TICKETS:
            return False
        USED_TICKETS[ticket] = now + 600
        return True


def allowed_url(value: str) -> bool:
    if value != value.strip() or any(ord(ch) <= 0x20 or ord(ch) == 0x7f for ch in value):
        return False
    if "\\" in value:
        return False

    parsed = urlparse(value)
    if parsed.scheme != "http":
        return False
    if parsed.username or parsed.password:
        return False
    if parsed.fragment:
        return False
    if parsed.hostname not in {"127.0.0.1", "localhost"}:
        return False
    if parsed.path.startswith("//"):
        return False
    try:
        port = parsed.port or 80
    except ValueError:
        return False
    return port == SITE_PORT


def open_page(url: str) -> None:
    with LIMIT:
        with tempfile.TemporaryDirectory(prefix="folio-browser-") as profile:
            env = os.environ.copy()
            env["HOME"] = profile
            env["MOZ_HEADLESS"] = "1"
            subprocess.run(
                [
                    "timeout",
                    "12s",
                    "firefox-esr",
                    "--headless",
                    "--new-instance",
                    "--no-remote",
                    "--profile",
                    profile,
                    url,
                ],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )


class Handler(BaseHTTPRequestHandler):
    server_version = "FolioReview/1.0"

    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        ticket = make_ticket()
        self._html(200, self.form(ticket))

    def do_POST(self):
        size = min(int(self.headers.get("Content-Length", "0")), 8192)
        data = parse_qs(self.rfile.read(size).decode("utf-8", "replace"))
        url = data.get("url", [""])[0]
        ticket = data.get("ticket", [""])[0]
        stamp = data.get("stamp", [""])[0]

        if not check_ticket(ticket) or not check_stamp(ticket, stamp):
            self._html(400, "<p>Stamp rejected.</p>")
            return
        if not allowed_url(url):
            self._html(400, "<p>Only the local preview port is accepted.</p>")
            return
        if not consume_ticket(ticket):
            self._html(400, "<p>Stamp already used.</p>")
            return

        threading.Thread(target=open_page, args=(url,), daemon=True).start()
        self._html(200, "<p>Queued.</p>")

    def form(self, ticket: str) -> str:
        sample = html.escape(f"sha256(ticket + ':' + stamp) starts with {'0' * DIFFICULTY}")
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Folio Review</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 40px; max-width: 760px; color: #1f2933; }}
    label {{ display: grid; gap: 8px; margin: 18px 0; font-weight: 650; }}
    input {{ padding: 11px; border: 1px solid #cbd5df; border-radius: 6px; font: inherit; }}
    button {{ border: 0; border-radius: 6px; padding: 11px 16px; background: #0f766e; color: white; font: inherit; font-weight: 700; }}
    code {{ word-break: break-word; }}
  </style>
</head>
<body>
  <h1>Folio Review</h1>
  <p><code>{sample}</code></p>
  <form method="post">
    <input type="hidden" name="ticket" value="{html.escape(ticket)}">
    <label>Preview URL<input name="url" placeholder="http://127.0.0.1:8080/view.php?id=..." required></label>
    <label>Ticket<input value="{html.escape(ticket)}" readonly></label>
    <label>Stamp<input name="stamp" required></label>
    <button type="submit">Send</button>
  </form>
</body>
</html>"""

    def _html(self, status: int, body: str):
        raw = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
