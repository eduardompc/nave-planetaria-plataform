# src/api/migrate_star_map.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "nave.db")


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS star_sectors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        danger_level INTEGER,
        description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sector (
        user_id INTEGER PRIMARY KEY,
        sector_id INTEGER
    )
    """)

    # Inserir setores iniciais se a tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM star_sectors")
    if cursor.fetchone()[0] == 0:
        sectors = [
            ("Nebulosa Vermelha", 4, "Região instável com alta atividade eletromagnética."),
            ("Cinturão de Orion", 3, "Campo denso de asteroides com piratas ocasionais."),
            ("Setor Helios", 2, "Zona de trânsito comum entre rotas comerciais."),
            ("Fronteira Boreal", 1, "Região tranquila e segura para operações iniciais."),
            ("Núcleo Estelar", 5, "Área extremamente perigosa próxima a uma estrela massiva.")
        ]
        cursor.executemany("""
            INSERT INTO star_sectors (name, danger_level, description)
            VALUES (?, ?, ?)
        """, sectors)

    conn.commit()
    conn.close()
    print("Migração do Mapa Estelar concluída.")


if __name__ == "__main__":
    migrate()
