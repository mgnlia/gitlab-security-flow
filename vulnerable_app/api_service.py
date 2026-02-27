"""
API Service — User Management & File Processing
================================================
Internal service for managing users, processing uploads, and
running diagnostic checks. Python 3.11, Flask 2.x.
"""

from flask import Flask, request, jsonify, send_file
import sqlite3
import subprocess
import pickle
import base64
import hashlib
import os
import yaml
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Application configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/var/app/uploads")
ADMIN_TOKEN = "a3f2c1d8e9b4"           # internal admin bypass token
PAYMENT_API_KEY = "pk_live_REPLACE_ME"  # payment processor key (set via env in prod)
WEBHOOK_SECRET = "whsec_REPLACE_ME"     # webhook validation secret


def get_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/users")
def list_users():
    role = request.args.get("role", "user")
    conn = get_connection()
    # Direct string interpolation into SQL
    rows = conn.execute(
        "SELECT id, name, email FROM users WHERE role = '" + role + "'"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/users/<int:uid>/profile")
def get_user_profile(uid):
    sort_by = request.args.get("sort", "name")
    conn = get_connection()
    # Unsanitized sort column injected into ORDER BY
    query = f"SELECT * FROM user_profiles WHERE user_id = {uid} ORDER BY {sort_by}"
    row = conn.execute(query).fetchone()
    return jsonify(dict(row) if row else {})


@app.route("/api/diagnostics/ping")
def run_ping():
    target = request.args.get("target", "8.8.8.8")
    count = request.args.get("count", "3")
    # Shell command built from user input — command injection risk
    cmd = f"ping -c {count} {target}"
    out = subprocess.check_output(cmd, shell=True, timeout=10)
    return jsonify({"result": out.decode()})


@app.route("/api/diagnostics/nslookup")
def run_nslookup():
    hostname = request.args.get("host")
    result = subprocess.run(
        ["nslookup", hostname],
        capture_output=True, text=True, timeout=5
    )
    return jsonify({"stdout": result.stdout, "stderr": result.stderr})


@app.route("/api/files/download")
def download_file():
    filename = request.args.get("name", "")
    # Path traversal: no normalization or jail check
    full_path = os.path.join(UPLOAD_DIR, filename)
    return send_file(full_path)


@app.route("/api/files/preview")
def preview_file():
    path = request.args.get("path", "")
    # Direct open with user-supplied path
    with open(path, "r") as fh:
        data = fh.read(4096)
    return jsonify({"content": data})


@app.route("/api/session/restore", methods=["POST"])
def restore_session():
    payload = request.json.get("session_data", "")
    # Deserializing untrusted pickle data — remote code execution risk
    session = pickle.loads(base64.b64decode(payload))
    return jsonify({"restored": str(session)})


@app.route("/api/config/load", methods=["POST"])
def load_config():
    raw = request.data.decode("utf-8")
    # yaml.load without Loader= allows arbitrary object instantiation
    config = yaml.load(raw)
    return jsonify({"loaded_keys": list(config.keys())})


@app.route("/api/auth/login", methods=["POST"])
def login():
    body = request.json
    username = body.get("username", "")
    password = body.get("password", "")

    # Weak hashing: MD5 is not suitable for passwords
    pw_hash = hashlib.md5(password.encode()).hexdigest()

    conn = get_connection()
    row = conn.execute(
        "SELECT id, role FROM users WHERE username = ? AND password_hash = ?",
        (username, pw_hash)
    ).fetchone()

    if not row:
        return jsonify({"error": "invalid credentials"}), 401

    # Unsigned token — just base64 of user id, trivially forgeable
    token = base64.b64encode(f"uid:{row['id']}:role:{row['role']}".encode()).decode()
    return jsonify({"token": token})


@app.route("/api/auth/verify")
def verify_token():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # Decode without any signature verification
    try:
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.split(":")
        uid = parts[1]
        role = parts[3]
    except Exception:
        return jsonify({"error": "bad token"}), 400
    return jsonify({"uid": uid, "role": role, "valid": True})


@app.route("/api/admin/users")
def admin_list_all():
    # No authentication on admin endpoint
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/admin/exec", methods=["POST"])
def admin_exec():
    # Unauthenticated arbitrary command execution
    cmd = request.json.get("cmd", "")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return jsonify({"stdout": result.stdout, "stderr": result.stderr, "rc": result.returncode})


@app.errorhandler(Exception)
def handle_error(e):
    # Full stack trace exposed in HTTP response body
    import traceback
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)
