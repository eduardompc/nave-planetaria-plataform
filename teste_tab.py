import sqlite3
conn = sqlite3.connect("nave.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(profiles)")
print(cursor.fetchall())
conn.close()
