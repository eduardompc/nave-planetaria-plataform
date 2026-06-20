from .db import get_connection

def save_telemetry(user_id, lat, lon, altitude, velocity):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO telemetry (user_id, lat, lon, altitude, velocity)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, lat, lon, altitude, velocity))

    conn.commit()
    conn.close()

def get_last_points(user_id, limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM telemetry
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_telemetry(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM telemetry
        WHERE user_id = ?
        ORDER BY timestamp ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows
