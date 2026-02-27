"""
Intentionally Vulnerable Auth Module
=====================================
Vulnerabilities:
- CWE-327: Weak cryptographic algorithm (MD5 for passwords)
- CWE-916: Insufficient password hashing iterations
- CWE-307: Improper restriction of login attempts (no rate limiting)
- CWE-613: Insufficient session expiration
"""

import hashlib
import hmac
import time
import os


# CWE-798: Hardcoded JWT secret
JWT_SECRET = "jwt-secret-key-hardcoded"

# CWE-327: MD5 is cryptographically broken for password hashing
def hash_password(password: str) -> str:
    """VULNERABLE: MD5 is not suitable for password hashing."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """VULNERABLE: timing attack possible — no constant-time comparison."""
    return hash_password(password) == stored_hash


# CWE-307: No rate limiting or lockout
def login(username: str, password: str, db) -> dict:
    """VULNERABLE: unlimited login attempts — brute force possible."""
    cursor = db.cursor()
    # CWE-89: SQL injection in login
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    user = cursor.fetchone()

    if user and verify_password(password, user["password_hash"]):
        # CWE-613: Token never expires
        token = generate_token(user["id"])
        return {"success": True, "token": token}
    return {"success": False}


def generate_token(user_id: int) -> str:
    """VULNERABLE: predictable token, no expiry, MD5-based."""
    # CWE-338: Cryptographically weak PRNG
    token_data = f"{user_id}:{time.time()}"
    return hashlib.md5(token_data.encode()).hexdigest()


def verify_token(token: str, db) -> dict:
    """VULNERABLE: no expiry check, no signature verification."""
    cursor = db.cursor()
    # CWE-89: SQL injection in token lookup
    query = f"SELECT * FROM users WHERE session_token = '{token}'"
    cursor.execute(query)
    return cursor.fetchone()
