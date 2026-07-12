import base64
import hashlib
import hmac
import json
import os
import re
import sqlite3
import threading
import time
from collections.abc import Mapping
from pathlib import Path

from ecdsa.curves import BRAINPOOLP512r1
from ecdsa.numbertheory import inverse_mod
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / os.environ.get("SINGEN_DATA_DIR", "data")
STATE_PATH = DATA_DIR / "state.json"
DB_PATH = DATA_DIR / "singen.sqlite3"

MAX_ACCOUNT_CHARS = 0x9999
STORED_ACCOUNT_CHARS = 0x10000
ACCOUNT_RE = re.compile(r"^[a-z0-9]+@.+\..+$", re.IGNORECASE | re.ASCII)
ADMIN_ACCOUNT = "whale@whale-tw.com"

CURVE = BRAINPOOLP512r1
GENERATOR = CURVE.generator
ORDER = GENERATOR.order()
ORDER_BYTES = (ORDER.bit_length() + 7) // 8
NONCE_PREFIX_BYTES = 48
NONCE_TAIL_BYTES = 16

TARGET_MESSAGE = "SinGen Said: At sunrise, when it answers over my signal, I sit by the sun."
DEFAULT_FLAG = "NHNC{TEST_ME}"

PHRASE_OPTIONS = {
    "time": [
        "night",
        "midnight",
        "sunrise",
        "blue hour",
        "last call",
        "the encore",
        "rain check",
        "golden hour",
        "half past forever",
        "the quiet shift",
        "opening time",
        "closing time",
        "moonrise",
        "noon",
        "afterglow",
        "rush hour",
        "curfew",
        "soft launch",
        "daybreak",
        "late checkout",
        "prime time",
        "tea time",
        "high tide",
        "low tide",
        "the long intro",
        "the bridge",
        "the chorus",
        "the prelude",
        "the fadeout",
        "the warm-up",
        "the afterparty",
        "the loading screen",
        "the coffee break",
        "the dress rehearsal",
        "the station delay",
        "the quiet reboot",
        "the tiny drum solo",
        "the cloud backup",
        "the keyboard nap",
        "the last train",
        "the open window",
        "the calendar reminder",
        "the midnight snack",
        "the porch light",
        "the firefly hour",
        "the silver minute",
        "the sleepy headline",
        "the soft alarm",
        "the empty platform",
        "the second verse",
    ],
    "motion": [
        "glows",
        "falls",
        "shines",
        "spills",
        "crashes",
        "turns",
        "drifts",
        "slides",
        "hums",
        "dances",
        "waits",
        "rolls",
        "breathes",
        "flickers",
        "wanders",
        "rises",
        "listens",
        "echoes",
        "melts",
        "whispers",
        "sparkles",
        "travels",
        "stretches",
        "rings",
        "pauses",
        "skips",
        "restarts",
        "buffers",
        "moonwalks",
        "sneezes",
        "overthinks",
        "autotunes",
        "tap-dances",
        "misplaces",
        "photobombs",
        "recalculates",
        "subscribes",
        "unsubscribes",
        "side-eyes",
        "daydreams",
        "freezes",
        "refreshes",
        "applauds",
        "stargazes",
        "checks in",
        "checks out",
        "wakes",
        "counts down",
        "signs off",
        "comes back",
    ],
    "place": [
        "room",
        "window",
        "radio",
        "keyboard",
        "notebook",
        "garden",
        "station",
        "balcony",
        "skyline",
        "record player",
        "coffee cup",
        "paper moon",
        "old guitar",
        "empty inbox",
        "blue sweater",
        "city map",
        "desk lamp",
        "front door",
        "headphones",
        "piano bench",
        "train ticket",
        "orange tree",
        "movie poster",
        "silent phone",
        "left shoe",
        "laundry pile",
        "spare charger",
        "weather app",
        "pizza box",
        "rubber duck",
        "sticky note",
        "alarm clock",
        "tiny cactus",
        "shipping label",
        "paper straw",
        "broken umbrella",
        "lucky coin",
        "bus schedule",
        "mirror",
        "raincoat",
        "server rack",
        "standing desk",
        "studio wall",
        "record sleeve",
        "blank postcard",
        "polaroid",
        "telescope",
        "floorboard",
        "doorbell",
        "sun chart",
    ],
    "seat": [
        "myself",
        "the window",
        "the river",
        "the console",
        "the speaker",
        "the stairwell",
        "the shore",
        "the back row",
        "the front step",
        "the phone",
        "the piano",
        "the skyline",
        "the porch",
        "the signal",
        "the station",
        "the turntable",
        "the monitor",
        "the old couch",
        "the open tab",
        "the quiet aisle",
        "the tiny fan",
        "the snack drawer",
        "the wrong gate",
        "the group chat",
        "the printer queue",
        "the empty mug",
        "the house plant",
        "the elevator music",
        "the coat rack",
        "the cookie tin",
        "the mail slot",
        "the dashboard",
        "the backup drive",
        "the loading bar",
        "the night bus",
        "the ticket booth",
        "the kitchen light",
        "the balcony rail",
        "the station clock",
        "the blue chair",
        "the glass door",
        "the window seat",
        "the record crate",
        "the pencil cup",
        "the moon map",
        "the lighthouse",
        "the rooftop",
        "the empty stage",
        "the sun dial",
        "the final note",
    ],
}


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64u_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def random_scalar() -> int:
    while True:
        value = int.from_bytes(os.urandom(ORDER_BYTES + 16), "big") % ORDER
        if value:
            return value


def load_state() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists():
        state = json.loads(STATE_PATH.read_text())
        changed = False
        if "admin_password" not in state:
            state["admin_password"] = b64u(os.urandom(64))
            changed = True
        if changed:
            tmp_path = STATE_PATH.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(state, indent=2, sort_keys=True))
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, STATE_PATH)
        return state

    state = {
        "admin_password": b64u(os.urandom(64)),
        "session_key": b64u(os.urandom(64)),
        "password_pepper": b64u(os.urandom(32)),
        "nonce_salt": b64u(os.urandom(32)),
        "signing_scalar": hex(random_scalar()),
    }
    tmp_path = STATE_PATH.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(state, indent=2, sort_keys=True))
    os.chmod(tmp_path, 0o600)
    os.replace(tmp_path, STATE_PATH)
    return state


STATE = load_state()
SESSION_KEY = b64u_decode(STATE["session_key"])
PASSWORD_PEPPER = b64u_decode(STATE["password_pepper"])
NONCE_SALT = b64u_decode(STATE["nonce_salt"])
ADMIN_PASSWORD = STATE["admin_password"]
SIGNING_SCALAR = int(STATE["signing_scalar"], 16)
VERIFY_POINT = SIGNING_SCALAR * GENERATOR

app = Flask(__name__)
app.secret_key = SESSION_KEY
register_guard = threading.Lock()


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with connect_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account TEXT NOT NULL,
                account_fingerprint TEXT NOT NULL UNIQUE,
                password_salt BLOB NOT NULL,
                password_hash BLOB NOT NULL,
                created_at INTEGER NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_users_account ON users(account);

            CREATE TABLE IF NOT EXISTS generated_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                message TEXT NOT NULL,
                token TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            """
        )
        ensure_admin_user(conn)


def ensure_admin_user(conn: sqlite3.Connection) -> None:
    fingerprint = account_fingerprint(ADMIN_ACCOUNT)
    exists = conn.execute(
        "SELECT 1 FROM users WHERE account_fingerprint = ?",
        (fingerprint,),
    ).fetchone()
    if exists is not None:
        return

    salt = os.urandom(16)
    conn.execute(
        """
        INSERT INTO users (account, account_fingerprint, password_salt, password_hash, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            stored_account(ADMIN_ACCOUNT),
            fingerprint,
            salt,
            hash_password(ADMIN_PASSWORD, salt),
            int(time.time()),
        ),
    )


def check_account(value: str) -> tuple[bool, str]:
    account = (value or "").strip()
    if not account or len(account) >= MAX_ACCOUNT_CHARS:
        return False, ""
    if ACCOUNT_RE.fullmatch(account) is None:
        return False, ""
    return True, account.lower()


def stored_account(account: str) -> str:
    return account[:STORED_ACCOUNT_CHARS]


def account_fingerprint(account: str) -> str:
    return hashlib.sha256(account.encode("utf-8")).hexdigest()


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8") + PASSWORD_PEPPER,
        salt,
        200_000,
    )


def find_user_by_id(user_id: int) -> sqlite3.Row | None:
    with connect_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def current_user() -> sqlite3.Row | None:
    user_id = session.get("uid")
    if not isinstance(user_id, int):
        return None
    return find_user_by_id(user_id)


def require_user():
    user = current_user()
    if user is None:
        return None, redirect(url_for("index"))
    return user, None


def canonical_payload(account: str, message: str) -> str:
    return json.dumps(
        {"account": account, "message": message},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def message_hash(account: str, message: str) -> int:
    data = canonical_payload(account, message).encode("utf-8")
    return int.from_bytes(hashlib.sha512(data).digest(), "big")


def nonce_for_account(account: str) -> int:
    prefix = hashlib.sha384(NONCE_SALT + account.encode("utf-8")).digest()
    while True:
        raw = prefix + os.urandom(NONCE_TAIL_BYTES)
        value = int.from_bytes(raw, "big") % ORDER
        if value:
            return value


def sign_parts(message: str, account: str) -> tuple[int, int]:
    z = message_hash(account, message)
    while True:
        k = nonce_for_account(account)
        point = k * GENERATOR
        r = point.x() % ORDER
        if not r:
            continue
        s = (inverse_mod(k, ORDER) * (z + r * SIGNING_SCALAR)) % ORDER
        if s:
            return r, s


def pack_token(account: str, message: str, r: int, s: int) -> str:
    payload = canonical_payload(account, message).encode("utf-8")
    signature = r.to_bytes(ORDER_BYTES, "big") + s.to_bytes(ORDER_BYTES, "big")
    return f"singen.{b64u(payload)}.{b64u(signature)}"


def unpack_token(token: str) -> tuple[str, str, int, int]:
    parts = (token or "").strip().split(".")
    if len(parts) != 3 or parts[0] != "singen":
        raise ValueError("bad token")
    payload = json.loads(b64u_decode(parts[1]).decode("utf-8"))
    account = payload.get("account")
    message = payload.get("message")
    if not isinstance(account, str) or not isinstance(message, str):
        raise ValueError("bad payload")
    expected_payload = canonical_payload(account, message).encode("utf-8")
    if not hmac.compare_digest(expected_payload, b64u_decode(parts[1])):
        raise ValueError("bad payload")
    signature = b64u_decode(parts[2])
    if len(signature) != ORDER_BYTES * 2:
        raise ValueError("bad signature")
    r = int.from_bytes(signature[:ORDER_BYTES], "big")
    s = int.from_bytes(signature[ORDER_BYTES:], "big")
    return account, message, r, s


def verify_parts(account: str, message: str, r: int, s: int) -> bool:
    if not (1 <= r < ORDER and 1 <= s < ORDER):
        return False
    z = message_hash(account, message)
    w = inverse_mod(s, ORDER)
    u1 = (z * w) % ORDER
    u2 = (r * w) % ORDER
    point = u1 * GENERATOR + u2 * VERIFY_POINT
    if point.x() is None:
        return False
    return point.x() % ORDER == r


def make_message(account: str, selected: dict[str, int]) -> str:
    speaker = account.split("@", 1)[0][:24] or "Singer"
    speaker = speaker[:1].upper() + speaker[1:]
    time_word = PHRASE_OPTIONS["time"][selected["time"]]
    motion_word = PHRASE_OPTIONS["motion"][selected["motion"]]
    place_word = PHRASE_OPTIONS["place"][selected["place"]]
    seat_word = PHRASE_OPTIONS["seat"][selected["seat"]]
    return f"{speaker} Said: At {time_word}, when it {motion_word} over my {place_word}, I sit by {seat_word}."


def parse_selected(source) -> dict[str, int]:
    selected: dict[str, int] = {}
    for key, values in PHRASE_OPTIONS.items():
        raw = source.get(key)
        if raw is None:
            raise ValueError("missing selection")
        try:
            index = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("bad selection") from exc
        if index < 0 or index >= len(values):
            raise ValueError("bad selection")
        selected[key] = index
    return selected


def generated_for_user(user_id: int) -> sqlite3.Row | None:
    with connect_db() as conn:
        return conn.execute(
            "SELECT * FROM generated_lines WHERE user_id = ?",
            (user_id,),
        ).fetchone()


def create_line(user: sqlite3.Row, selected: dict[str, int]) -> sqlite3.Row:
    message = make_message(user["account"], selected)
    r, s = sign_parts(message, user["account"])
    token = pack_token(user["account"], message, r, s)
    now = int(time.time())
    with connect_db() as conn:
        conn.execute(
            "INSERT INTO generated_lines (user_id, message, token, created_at) VALUES (?, ?, ?, ?)",
            (user["id"], message, token, now),
        )
        return conn.execute(
            "SELECT * FROM generated_lines WHERE user_id = ?",
            (user["id"],),
        ).fetchone()


@app.get("/")
def index():
    if current_user() is not None:
        return redirect(url_for("studio"))
    return render_template("index.html")


@app.post("/register")
def register():
    ok, account = check_account(request.form.get("email", ""))
    password = request.form.get("password", "")
    if not ok:
        flash("Use a valid email-style account.")
        return redirect(url_for("index"))
    if len(password) < 8:
        flash("Use at least 8 characters for the password.")
        return redirect(url_for("index"))

    salt = os.urandom(16)
    password_hash = hash_password(password, salt)
    fingerprint = account_fingerprint(account)
    now = int(time.time())

    with register_guard:
        conn = connect_db()
        try:
            conn.execute("BEGIN IMMEDIATE")
            exists = conn.execute(
                "SELECT 1 FROM users WHERE account_fingerprint = ?",
                (fingerprint,),
            ).fetchone()
            if exists is not None:
                conn.rollback()
                flash("That account is already registered.")
                return redirect(url_for("index"))
            conn.execute(
                """
                INSERT INTO users (account, account_fingerprint, password_salt, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (stored_account(account), fingerprint, salt, password_hash, now),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("That account is already registered.")
            return redirect(url_for("index"))
        finally:
            conn.close()

    flash("Account created. Please sign in.")
    return redirect(url_for("index"))


@app.post("/login")
def login():
    ok, account = check_account(request.form.get("email", ""))
    password = request.form.get("password", "")
    if not ok:
        flash("Check your account and password.")
        return redirect(url_for("index"))

    with connect_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE account_fingerprint = ?",
            (account_fingerprint(account),),
        ).fetchone()

    if user is None:
        flash("Check your account and password.")
        return redirect(url_for("index"))
    expected = hash_password(password, user["password_salt"])
    if not hmac.compare_digest(expected, user["password_hash"]):
        flash("Check your account and password.")
        return redirect(url_for("index"))

    session.clear()
    session["uid"] = int(user["id"])
    return redirect(url_for("studio"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.get("/studio")
def studio():
    user, response = require_user()
    if response is not None:
        return response
    line = generated_for_user(user["id"])
    return render_template(
        "studio.html",
        user=user,
        line=line,
        options=PHRASE_OPTIONS,
        target_message=TARGET_MESSAGE,
    )


@app.post("/generate")
def generate():
    user, response = require_user()
    if response is not None:
        return response
    if generated_for_user(user["id"]) is not None:
        flash("This account already has a generated line.")
        return redirect(url_for("studio"))
    try:
        selected = parse_selected(request.form)
        create_line(user, selected)
    except (sqlite3.IntegrityError, ValueError):
        flash("The selected line could not be generated.")
    return redirect(url_for("studio"))


@app.get("/verify")
def verify_page():
    return render_template("verify.html", target_message=TARGET_MESSAGE, result=None)


@app.post("/verify")
def verify_submit():
    token = request.form.get("token", "")
    result = verify_token(token)
    return render_template("verify.html", target_message=TARGET_MESSAGE, result=result, token=token)


def verify_token(token: str) -> dict:
    try:
        account, message, r, s = unpack_token(token)
    except Exception:
        return {"ok": False, "message": "Token format was not accepted."}
    if not verify_parts(account, message, r, s):
        return {"ok": False, "message": "Signature check failed."}
    if account == ADMIN_ACCOUNT:
        return {"ok": True, "message": message, "flag": os.environ.get("FLAG", DEFAULT_FLAG)}
    return {"ok": True, "message": message}


@app.get("/api/info")
def api_info():
    return jsonify(
        {
            "name": "SinGen",
            "curve": "BrainpoolP512r1",
            "order": str(ORDER),
            "order_bytes": ORDER_BYTES,
            "nonce_tail_bits": NONCE_TAIL_BYTES * 8,
            "stored_account_chars": STORED_ACCOUNT_CHARS,
            "max_account_chars": MAX_ACCOUNT_CHARS,
            "admin_account": ADMIN_ACCOUNT,
            "target": TARGET_MESSAGE,
        }
    )


@app.post("/api/generate")
def api_generate():
    user, response = require_user()
    if response is not None:
        return jsonify({"ok": False, "error": "sign in required"}), 401
    line = generated_for_user(user["id"])
    if line is None:
        payload = request.get_json(silent=True) or request.form
        if not isinstance(payload, Mapping):
            return jsonify({"ok": False, "error": "bad selection"}), 400
        try:
            selected = parse_selected(payload)
            line = create_line(user, selected)
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "error": "line already generated"}), 409
        except ValueError:
            return jsonify({"ok": False, "error": "bad selection"}), 400
    return jsonify({"ok": True, "message": line["message"], "token": line["token"]})


@app.post("/api/verify")
def api_verify():
    payload = request.get_json(silent=True) or request.form
    if not isinstance(payload, Mapping):
        return jsonify({"ok": False, "message": "Token format was not accepted."}), 400
    token = payload.get("token", "")
    result = verify_token(token)
    status = 200 if result.get("ok") else 400
    return jsonify(result), status


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
