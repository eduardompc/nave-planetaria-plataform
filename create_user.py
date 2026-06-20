from src.api.db import get_connection
from src.auth.security import hash_password

username = "comandante"
password = "1234"

conn = get_connection()
cursor = conn.cursor()

password_hash = hash_password(password)

cursor.execute("""
    INSERT INTO users (username, password_hash)
    VALUES (?, ?)
""", (username, password_hash))

conn.commit()
conn.close()

print("Usuário criado com sucesso!")
