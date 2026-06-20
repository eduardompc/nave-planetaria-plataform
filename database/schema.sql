PRAGMA foreign_keys = ON;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de perfis
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rank TEXT DEFAULT 'Cadete',
    xp INTEGER DEFAULT 0,
    theme_preference TEXT DEFAULT 'auto',
    theme TEXT DEFAULT 'auto',
    last_login TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de missões
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mission_name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de telemetria
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lat REAL,
    lon REAL,
    altitude REAL,
    velocity REAL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de logs internos
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    type TEXT DEFAULT 'info',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Tabela de contexto IA
CREATE TABLE IF NOT EXISTS ai_context (
    context_key TEXT PRIMARY KEY,
    context_value TEXT,
    updated_at TEXT
);

-- Tabela de memória IA
CREATE TABLE IF NOT EXISTS ai_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    memory TEXT,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabela de setores estelares
CREATE TABLE IF NOT EXISTS star_sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    danger_level INTEGER,
    description TEXT
);

-- Tabela de setor atual do usuário
CREATE TABLE IF NOT EXISTS user_sector (
    user_id INTEGER PRIMARY KEY,
    sector_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (sector_id) REFERENCES star_sectors(id) ON DELETE SET NULL
);

-- Nova Tabela de Objetos Celestes (Planetas, Estrelas, Constelações)
CREATE TABLE IF NOT EXISTS celestial_objects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL, -- 'planet', 'star', 'constellation'
    constellation TEXT,
    distance_ly REAL,
    magnitude REAL,
    description TEXT,
    coordinates_json TEXT
);

-- Nova Tabela de Observações dos Usuários (Gamificação)
CREATE TABLE IF NOT EXISTS user_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    object_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (object_id) REFERENCES celestial_objects(id) ON DELETE CASCADE,
    UNIQUE(user_id, object_id)
);
