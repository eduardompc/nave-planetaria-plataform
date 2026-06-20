from .db import get_connection
from datetime import datetime

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

def update_last_login(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET last_login = ?
        WHERE user_id = ?
    """, (datetime.now(), user_id))

    conn.commit()
    conn.close()

def add_xp(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET xp = xp + ?
        WHERE user_id = ?
    """, (amount, user_id))

    conn.commit()
    conn.close()

def set_theme(user_id, theme):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE profiles
        SET theme_preference = ?
        WHERE user_id = ?
    """, (theme, user_id))

    conn.commit()
    conn.close()
    
def create_profile_if_missing(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()

    if not profile:
        cursor.execute("""
            INSERT INTO profiles (user_id, xp, theme_preference, last_login)
            VALUES (?, 0, 'auto', ?)
        """, (user_id, None))
        conn.commit()

    conn.close()

