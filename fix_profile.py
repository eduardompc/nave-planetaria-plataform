from src.api.db import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("ALTER TABLE profiles RENAME COLUMN theme_preference TO theme")

conn.commit()
conn.close()

print("Coluna renomeada com sucesso!")
