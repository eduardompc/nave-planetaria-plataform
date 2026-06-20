import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash) -> bool:
    if isinstance(password_hash, str):
        password_hash = password_hash.encode('utf-8')
    elif isinstance(password_hash, memoryview):
        password_hash = password_hash.tobytes()
    elif isinstance(password_hash, bytes):
        pass
    return bcrypt.checkpw(password.encode(), password_hash)
