import sqlite3
conn = sqlite3.connect("nave.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0,
    theme_preference TEXT DEFAULT 'auto',
    last_login TEXT DEFAULT 'Primeiro acesso',
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()
