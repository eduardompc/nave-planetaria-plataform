from src.api.db import get_connection
from src.auth.security import hash_password

conn = get_connection()
cursor = conn.cursor()

# Remove o usuário antigo
cursor.execute("DELETE FROM users WHERE username = 'comandante'")

# Cria novamente com a senha correta
password_hash = hash_password("1234")

cursor.execute("""
    INSERT INTO users (username, password_hash)
    VALUES (?, ?)
""", ("comandante", password_hash))

conn.commit()
conn.close()

print("Usuário 'comandante' recriado com sucesso!")
