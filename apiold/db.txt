import sqlite3

def get_connection():
    conn = sqlite3.connect("database/nave.db")
    conn.row_factory = sqlite3.Row  # ← ESSENCIAL
    return conn
