import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

try:
    print("Testing connection with encoded password...")
    # Aikaluna@24 -> Aikaluna%4024
    conn = psycopg2.connect("postgresql://postgres:Aikaluna%4024@localhost:5432/postgres")
    print("Connected successfully to 'postgres' database!")
    
    # Try to create database 'nave_db' if it does not exist
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'nave_db'")
    exists = cursor.fetchone()
    if not exists:
        print("Creating database 'nave_db'...")
        cursor.execute("CREATE DATABASE nave_db")
        print("Database 'nave_db' created successfully!")
    else:
        print("Database 'nave_db' already exists!")
    
    cursor.close()
    conn.close()
    print("TEST SUCCESSFUL")
except Exception as ex:
    print("Failed to connect or create database. Error:", ex)
    sys.exit(1)
