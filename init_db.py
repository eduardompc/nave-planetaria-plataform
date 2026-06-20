import dotenv
dotenv.load_dotenv()

from src.api.db import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    with open("database/schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("Banco inicializado com sucesso!")

if __name__ == "__main__":
    init_db()
