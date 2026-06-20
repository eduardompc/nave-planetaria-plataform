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
