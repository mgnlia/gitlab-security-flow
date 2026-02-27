"""
Intentionally Vulnerable Database Module
=========================================
Vulnerabilities for SecFlow demo:
- CWE-89:  SQL Injection (multiple)
- CWE-312: Cleartext storage of sensitive information
- CWE-259: Hardcoded password in connection string
"""

import sqlite3
import logging
import os

# CWE-259: Hardcoded DB credentials
DB_URL = "postgresql://admin:Password123!@prod-db.internal:5432/users"

# CWE-312: Logging sensitive data in cleartext
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_db(path: str = "users.db"):
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password_hash TEXT,
            email TEXT,
            session_token TEXT,
            credit_card TEXT
        )
    """)
    conn.commit()
    return conn


def get_user_by_id(conn, user_id: str):
    """CWE-89: Direct string interpolation — SQL injection."""
    # VULNERABLE
    query = f"SELECT * FROM users WHERE id = {user_id}"
    logger.debug(f"Executing query: {query}")  # CWE-312: logs query with user data
    return conn.execute(query).fetchone()


def get_user_by_email(conn, email: str):
    """CWE-89: SQL injection via email parameter."""
    # VULNERABLE
    query = "SELECT * FROM users WHERE email = '" + email + "'"
    return conn.execute(query).fetchone()


def update_password(conn, user_id: str, new_password_hash: str):
    """CWE-89: SQL injection in UPDATE statement."""
    # VULNERABLE
    query = f"UPDATE users SET password_hash = '{new_password_hash}' WHERE id = {user_id}"
    conn.execute(query)
    conn.commit()
    # CWE-312: Logging password hash
    logger.info(f"Password updated for user {user_id}: hash={new_password_hash}")


def store_credit_card(conn, user_id: int, card_number: str):
    """CWE-312: Storing credit card in plaintext."""
    # VULNERABLE: PCI-DSS violation — never store raw card numbers
    conn.execute(
        "INSERT INTO payments (user_id, card) VALUES (?, ?)",
        (user_id, card_number)  # should be tokenized/encrypted
    )
    conn.commit()
    logger.debug(f"Stored card for user {user_id}: {card_number}")  # logs PAN!
