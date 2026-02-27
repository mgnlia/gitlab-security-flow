"""
Intentionally Vulnerable Sample Application
============================================
This file contains DELIBERATE security vulnerabilities for testing the
GitLab Duo Security Orchestration Flow. DO NOT deploy to production.

Vulnerabilities present (for demo purposes):
- CWE-89: SQL Injection (lines 28, 45)
- CWE-78: Command Injection (line 62)
- CWE-798: Hardcoded Credentials (lines 15-17)
- CWE-22: Path Traversal (line 79)
- CWE-502: Insecure Deserialization (line 93)
"""

from flask import Flask, request, jsonify
import sqlite3
import os
import subprocess
import pickle
import base64

app = Flask(__name__)

# CWE-798: Hardcoded credentials — SECRET NEVER EXPIRES
SECRET_KEY = "super-secret-key-do-not-share-abc123"
DB_PASSWORD = "admin:password123@localhost/mydb"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"


def get_db():
    return sqlite3.connect("users.db")


@app.route("/user/<user_id>")
def get_user(user_id):
    """CWE-89: SQL Injection — user_id injected directly into query."""
    db = get_db()
    cursor = db.cursor()
    # VULNERABLE: f-string interpolation in SQL
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    return jsonify({"user": user})


@app.route("/search")
def search_users():
    """CWE-89: SQL Injection via search parameter."""
    name = request.args.get("name", "")
    db = get_db()
    cursor = db.cursor()
    # VULNERABLE: string concatenation in SQL
    query = "SELECT * FROM users WHERE name LIKE '%" + name + "%'"
    cursor.execute(query)
    results = cursor.fetchall()
    return jsonify({"results": results})


@app.route("/ping")
def ping_host():
    """CWE-78: Command Injection — host parameter passed to shell."""
    host = request.args.get("host", "localhost")
    # VULNERABLE: shell=True with user input
    result = subprocess.run(
        f"ping -c 1 {host}",
        shell=True,
        capture_output=True,
        text=True
    )
    return jsonify({"output": result.stdout})


@app.route("/file")
def read_file():
    """CWE-22: Path Traversal — no sanitization of file path."""
    filename = request.args.get("name", "readme.txt")
    base_dir = "/app/files/"
    # VULNERABLE: user controls path, can traverse to /etc/passwd etc.
    filepath = base_dir + filename
    with open(filepath, "r") as f:
        content = f.read()
    return jsonify({"content": content})


@app.route("/deserialize", methods=["POST"])
def deserialize_data():
    """CWE-502: Insecure Deserialization — pickle from user input."""
    data = request.json.get("data", "")
    # VULNERABLE: pickle.loads on untrusted data allows RCE
    obj = pickle.loads(base64.b64decode(data))
    return jsonify({"result": str(obj)})


@app.route("/admin")
def admin_panel():
    """CWE-306: Missing authentication for admin endpoint."""
    # VULNERABLE: no authentication check
    users = get_db().execute("SELECT * FROM users").fetchall()
    return jsonify({"all_users": users})


if __name__ == "__main__":
    # VULNERABLE: debug=True in production, binds to all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
