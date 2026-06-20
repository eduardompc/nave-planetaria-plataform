from .db import get_connection

def add_log(user_id, message, type="info"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (user_id, message, type)
        VALUES (?, ?, ?)
    """, (user_id, message, type))

    conn.commit()
    conn.close()

def get_recent_logs(user_id, limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM logs
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows
