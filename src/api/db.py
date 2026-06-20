import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "database", "nave.db"))
DATABASE_URL = os.environ.get("DATABASE_URL")

class DictRow(dict):
    def __init__(self, dict_data, list_data):
        super().__init__(dict_data)
        self.list_data = list_data

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.list_data[key]
        return super().__getitem__(key)

def make_row(cursor, values):
    if values is None:
        return None
    desc = cursor.description
    dict_data = {desc[i][0]: values[i] for i in range(len(desc))}
    return DictRow(dict_data, values)

class PostgresCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, sql, params=None):
        sql = sql.replace('?', '%s')
        if params is not None:
            self.cursor.execute(sql, params)
        else:
            self.cursor.execute(sql)
        return self

    def executemany(self, sql, seq_of_params):
        sql = sql.replace('?', '%s')
        self.cursor.executemany(sql, seq_of_params)
        return self

    def executescript(self, script_text):
        import re
        # Remove sqlite PRAGMAs
        script_text = re.sub(r'(?i)pragma\s+[^;]+;', '', script_text)
        # Convert AUTOINCREMENT to SERIAL
        script_text = re.sub(r'(?i)INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', script_text)
        self.cursor.execute(script_text)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return make_row(self.cursor, row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [make_row(self.cursor, r) for r in rows]

    @property
    def description(self):
        return self.cursor.description

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        return PostgresCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def execute(self, sql, params=None):
        cursor = self.cursor()
        cursor.execute(sql, params)
        return cursor

def get_connection():
    if DATABASE_URL:
        # Conexão PostgreSQL para nuvem/produção
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        return PostgresConnectionWrapper(conn)
    else:
        # Fallback local seguro usando SQLite
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except sqlite3.OperationalError:
            pass
        conn.row_factory = sqlite3.Row  # ← ESSENCIAL
        return conn
