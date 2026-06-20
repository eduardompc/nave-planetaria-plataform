# src/api/ai_memory.py
import sqlite3
import os
from datetime import datetime

from src.api.db import get_connection



def add_ai_memory(user_id, memory):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_memory (user_id, memory, timestamp)
        VALUES (?, ?, ?)
    """, (user_id, memory, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_ai_memory(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT memory, timestamp
        FROM ai_memory
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_ai_memory(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ai_memory WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def clear_all_ai_memory():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ai_memory")
    conn.commit()
    conn.close()
