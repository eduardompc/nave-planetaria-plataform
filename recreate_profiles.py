# recreate_profiles.py
from src.api.db import get_connection

def recreate_profiles_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Recria a tabela com a estrutura correta
    cursor.execute("DROP TABLE IF EXISTS profiles")
    cursor.execute("""
        CREATE TABLE profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            xp INTEGER DEFAULT 0,
            theme_preference TEXT DEFAULT 'auto',
            last_login TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Tabela 'profiles' recriada com sucesso!")

if __name__ == "__main__":
    recreate_profiles_table()