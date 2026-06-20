# migrate_profiles.py
from src.api.db import get_connection

def migrate_profiles_table():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verifica a estrutura atual da tabela
    cursor.execute("PRAGMA table_info(profiles)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Adiciona colunas faltantes
    if 'theme_preference' not in column_names:
        cursor.execute("ALTER TABLE profiles ADD COLUMN theme_preference TEXT DEFAULT 'auto'")
        print("Coluna 'theme_preference' adicionada")
    
    if 'last_login' not in column_names:
        cursor.execute("ALTER TABLE profiles ADD COLUMN last_login TEXT")
        print("Coluna 'last_login' adicionada")
    
    if 'xp' not in column_names:
        cursor.execute("ALTER TABLE profiles ADD COLUMN xp INTEGER DEFAULT 0")
        print("Coluna 'xp' adicionada")
    
    conn.commit()
    conn.close()
    print("Migração concluída!")

if __name__ == "__main__":
    migrate_profiles_table()