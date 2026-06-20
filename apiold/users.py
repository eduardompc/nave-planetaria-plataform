from .db import get_connection
from src.auth.security import hash_password, verify_password

def create_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
    """, (username, password_hash))

    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    conn.close()

    if not user:
        return None

    if verify_password(password, user["password_hash"]):
        return user

    return None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"]
    }
