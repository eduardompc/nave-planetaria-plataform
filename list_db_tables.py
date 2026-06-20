import sqlite3
conn = sqlite3.connect("database/nave.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database/nave.db:")
for table in tables:
    name = table[0]
    cursor.execute(f"PRAGMA table_info({name})")
    cols = [col[1] for col in cursor.fetchall()]
    print(f" - {name}: {cols}")
conn.close()
