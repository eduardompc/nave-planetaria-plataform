from .db import get_connection

def add_mission(user_id, mission_code, mission_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO missions (user_id, mission_name, status, progress)
        VALUES (?, ?, 'active', 0)
    """, (user_id, mission_name))

    conn.commit()
    conn.close()

def get_active_missions(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM missions
        WHERE user_id = ? AND status = 'active'
    """, (user_id,))
    missions = cursor.fetchall()

    conn.close()
    return missions

def update_mission_progress(mission_id, progress, status=None):
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute("""
            UPDATE missions
            SET progress = ?, status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (progress, status, mission_id))
    else:
        cursor.execute("""
            UPDATE missions
            SET progress = ?
            WHERE id = ?
        """, (progress, mission_id))

    conn.commit()
    conn.close()
