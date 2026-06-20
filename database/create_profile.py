from src.api.db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO profiles (user_id, rank, xp, theme, last_login)
    VALUES (?, ?, ?, ?, ?)
""", (1, "Comandante", 0, "auto", "Primeiro acesso"))

conn.commit()
conn.close()

print("Perfil do comandante criado com sucesso!")
