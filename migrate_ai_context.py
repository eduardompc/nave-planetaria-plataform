# src/api/migrate_ai_context.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "nave.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_context (
        context_key TEXT PRIMARY KEY,
        context_value TEXT,
        updated_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ai_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        memory TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Migração IA concluída.")


if __name__ == "__main__":
    migrate()
