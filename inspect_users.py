import sqlite3

conn = sqlite3.connect("database/nave.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
rows = cursor.fetchall()

for row in rows:
    print(row)
