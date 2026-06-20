from src.api.db import get_connection

conn = get_connection()
cursor = conn.cursor()

rows = cursor.execute("PRAGMA database_list").fetchall()

for row in rows:
    print(dict(row))
