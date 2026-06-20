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
