import json
from src.api.db import get_connection
from src.user.profile_manager import reward_user

def get_all_celestial_objects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM celestial_objects")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def get_observed_object_ids(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT object_id FROM user_observations WHERE user_id = ?", (user_id,))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def record_observation(user_id, object_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica se já está observado
    cursor.execute("""
        SELECT COUNT(*) FROM user_observations 
        WHERE user_id = ? AND object_id = ?
    """, (user_id, object_id))
    
    already_observed = cursor.fetchone()[0] > 0
    
    if not already_observed:
        # Registra observação
        cursor.execute("""
            INSERT INTO user_observations (user_id, object_id)
            VALUES (?, ?)
        """, (user_id, object_id))
        
        # Registra um log interno de conquista
        cursor.execute("SELECT name FROM celestial_objects WHERE id = ?", (object_id,))
        obj_name = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO logs (user_id, message, type)
            VALUES (?, ?, ?)
        """, (user_id, f"Objeto observado com sucesso no telescópio digital: {obj_name}", "info"))
        
        conn.commit()
        conn.close()
        
        # Recompensa o usuário com +50 XP
        reward_user(user_id, 50)
        return True
        
    conn.close()
    return False

def get_celestial_object_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM celestial_objects WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_celestial_object_by_id(object_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM celestial_objects WHERE id = ?", (object_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def reset_user_observations(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_observations WHERE user_id = ?", (user_id,))
    
    # Reseta o XP do perfil do usuário para 100
    cursor.execute("""
        UPDATE profiles
        SET xp = 100, rank = 'Cadete'
        WHERE user_id = ?
    """, (user_id,))
    
    cursor.execute("""
        INSERT INTO logs (user_id, message, type)
        VALUES (?, 'Progresso de observações científicas e XP resetados pelo piloto.', 'warning')
    """, (user_id,))
    
    conn.commit()
    conn.close()
