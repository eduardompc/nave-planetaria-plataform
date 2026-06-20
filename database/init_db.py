import os
import json
import math
from dotenv import load_dotenv
load_dotenv()

from src.api.db import get_connection
from src.auth.security import hash_password

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Executa o schema
    with open("database/schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # 1) Insere o usuário padrão e admin se não existirem
    # Comandante
    cursor.execute("SELECT id FROM users WHERE username = ?", ("comandante",))
    u_comandante = cursor.fetchone()
    if not u_comandante:
        password_hash = hash_password("1234")
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, ("comandante", password_hash))
        
        cursor.execute("SELECT id FROM users WHERE username = ?", ("comandante",))
        uid = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO profiles (user_id, rank, xp, theme_preference, theme, last_login)
            VALUES (?, 'Comandante', 100, 'auto', 'auto', ?)
        """, (uid, None))
        print("Usuário 'comandante' (senha '1234') criado com sucesso.")

    # Admin
    cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    u_admin = cursor.fetchone()
    if not u_admin:
        password_hash = hash_password("Aikaluna@24")
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, ("admin", password_hash))
        
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        uid = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO profiles (user_id, rank, xp, theme_preference, theme, last_login)
            VALUES (?, 'Comandante', 100, 'auto', 'auto', ?)
        """, (uid, None))
        print("Usuário 'admin' (senha 'Aikaluna@24') criado com sucesso.")

    # 2) Insere os setores estelares se vazio
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
        print("Setores estelares semeados.")

    # 3) Insere objetos celestes (planetas, estrelas) para o Catálogo e Mapa 3D
    cursor.execute("SELECT COUNT(*) FROM celestial_objects")
    if cursor.fetchone()[0] == 0:
        objects = []
        
        # --- PLANETAS DO SISTEMA SOLAR (Colocados no plano eclíptico central, R_proj < 12) ---
        planets = [
            # (Nome, tipo, constelação, dist_anos_luz, magnitude, desc, x, y, z)
            ("Sol", "planet", "Sistema Solar", 0.000016, -26.7, "Nossa estrela central, uma anã amarela do tipo espectral G2V.", 0.0, 0.0, 0.0),
            ("Mercúrio", "planet", "Sistema Solar", 0.000011, -0.42, "O menor e mais próximo planeta do Sol, extremamente denso.", 1.2, 0.5, 0.1),
            ("Vênus", "planet", "Sistema Solar", 0.000004, -4.6, "Planeta extremamente quente, coberto por densas nuvens de ácido sulfúrico.", -2.0, 1.5, -0.2),
            ("Terra", "planet", "Sistema Solar", 0.0, -3.0, "Nosso planeta natal, o único conhecido a abrigar vida ativa.", 3.0, 0.0, 0.0),
            ("Marte", "planet", "Sistema Solar", 0.000024, -1.5, "O Planeta Vermelho, desértico e com fina atmosfera de CO2.", -3.8, -2.5, 0.4),
            ("Júpiter", "planet", "Sistema Solar", 0.000066, -2.94, "O gigante gasoso, maior planeta do sistema, com sua Grande Mancha Vermelha.", 5.5, 4.2, -0.5),
            ("Saturno", "planet", "Sistema Solar", 0.00013, -0.2, "Famoso por seu espetacular e amplo sistema de anéis.", -7.2, -6.0, 1.0),
            ("Urano", "planet", "Sistema Solar", 0.00027, 5.38, "Gigante gelado com rotação inclinada quase paralela à sua órbita.", 9.5, 2.0, -1.2),
            ("Netuno", "planet", "Sistema Solar", 0.00043, 7.78, "O planeta mais distante do Sol, açoitado por ventos supersônicos.", -11.0, 8.5, 1.8),
        ]
        
        for name, otype, const, dist, mag, desc, x, y, z in planets:
            coords = {"x": x, "y": y, "z": z}
            objects.append((name, otype, const, dist, mag, desc, json.dumps(coords)))

        # --- ESTRELAS (Projetadas em uma esfera celeste de raio = 20) ---
        stars_raw = [
            # (Nome, RA_hours, Dec_degrees, Dist_LY, Mag, Constelação, Descrição)
            ("Sirius", 6.75, -16.7, 8.6, -1.46, "Cão Maior", "A estrela mais brilhante do céu noturno, uma estrela binária azul-branca."),
            ("Canopus", 6.4, -52.7, 310.0, -0.74, "Quilha", "Uma supergigante branco-amarelada, segunda estrela mais brilhante."),
            ("Rigel", 5.25, -8.2, 860.0, 0.13, "Orion", "Supergigante azul extremamente luminosa no pé da constelação de Orion."),
            ("Betelgeuse", 5.92, 7.4, 640.0, 0.5, "Orion", "Supergigante vermelha massiva próxima ao fim de seu ciclo estelar."),
            ("Vega", 18.62, 38.8, 25.0, 0.03, "Lira", "Estrela branca jovem, amplamente estudada, referência na escala de magnitude."),
            ("Polaris", 2.53, 89.3, 433.0, 1.97, "Ursa Menor", "A Estrela do Norte, utilizada há séculos para navegação marítima e aérea."),
            ("Aldebaran", 4.6, 16.5, 65.0, 0.85, "Taurus", "Uma gigante vermelha gigante que representa o olho brilhante do Touro."),
            ("Arcturus", 14.26, 19.1, 37.0, -0.05, "Boieiro", "Uma gigante laranja, a estrela mais brilhante do hemisfério celeste norte."),
            ("Capella", 5.28, 46.0, 42.0, 0.08, "Cocheiro", "Um sistema estelar quádruplo brilhante, composto por duas gigantes amarelas."),
            ("Procyon", 7.65, 5.2, 11.4, 0.34, "Cão Menor", "Uma subgigante branca, oitava estrela mais brilhante no céu noturno."),
            ("Altair", 19.84, 8.9, 16.7, 0.76, "Águia", "Estrela branca que gira tão rápido que seu equador se expande visivelmente."),
            ("Antares", 16.49, -26.4, 550.0, 1.06, "Escorpião", "Uma supergigante vermelha no coração da constelação do Escorpião."),
        ]
        
        R = 20.0 # Raio da esfera celeste no gráfico
        for name, ra, dec, dist, mag, const, desc in stars_raw:
            # Converte RA e Dec para coordenadas cartesianas 3D
            ra_rad = ra * (15.0 * math.pi / 180.0)
            dec_rad = dec * (math.pi / 180.0)
            
            x = R * math.cos(dec_rad) * math.cos(ra_rad)
            y = R * math.cos(dec_rad) * math.sin(ra_rad)
            z = R * math.sin(dec_rad)
            
            coords = {"x": round(x, 3), "y": round(y, 3), "z": round(z, 3)}
            objects.append((name, "star", const, dist, mag, desc, json.dumps(coords)))

        cursor.executemany("""
            INSERT INTO celestial_objects (name, type, constellation, distance_ly, magnitude, description, coordinates_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, objects)
        print("Objetos celestes catalogados e semeados.")

    conn.commit()
    conn.close()
    print("Banco inicializado e semeado com sucesso!")

if __name__ == "__main__":
    init_db()
