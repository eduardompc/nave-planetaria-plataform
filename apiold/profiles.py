from .db import get_connection

def create_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO profiles (user_id)
        VALUES (?)
    """, (user_id,))

    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()

    conn.close()
    return profile
