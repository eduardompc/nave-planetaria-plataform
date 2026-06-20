# src/api/ai_context.py
import sqlite3
import os
from datetime import datetime

from src.api.ai_memory import get_ai_memory, add_ai_memory

from src.api.db import get_connection



# ---------- CONTEXTO GLOBAL DA IA ----------

def get_ai_context():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT context_key, context_value FROM ai_context")
    rows = cursor.fetchall()
    conn.close()
    return {k: v for (k, v) in rows}


def update_ai_context(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ai_context (context_key, context_value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(context_key) DO UPDATE SET
            context_value = excluded.context_value,
            updated_at = excluded.updated_at
    """, (key, value, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


# ---------- BRIEFING CONTEXTUAL ----------

def generate_ai_briefing(user_id, profile, ship_status, sector, inventory):
    """
    Gera linhas de briefing da IA com base no contexto atual.
    """
    lines = []

    # 1) Situação da nave
    if ship_status:
        hull = ship_status.get("hull", 100)
        fuel = ship_status.get("fuel", 100)
        shields = ship_status.get("shields", 100)

        if hull < 30:
            lines.append("Atenção, piloto. A integridade do casco está crítica. Recomendo reparos imediatos.")
        elif hull < 60:
            lines.append("Casco com danos moderados. Uma passada no hangar pode ser uma boa ideia.")

        if fuel < 20:
            lines.append("Nível de combustível baixo. Sugiro reabastecer antes de avançar para outro setor.")
        elif fuel < 50:
            lines.append("Combustível em nível intermediário. Fique atento em viagens longas.")

        if shields < 30:
            lines.append("Escudos em nível crítico. Evite confrontos diretos até recarregar.")
        elif shields < 60:
            lines.append("Escudos parcialmente drenados. Recomendo recarga em breve.")

    # 2) Setor atual
    if sector:
        name = sector.get("name", "setor desconhecido")
        danger = sector.get("danger_level", 1)
        if danger >= 4:
            lines.append(f"Estamos em {name}, um setor de alto risco. Mantenha todos os sistemas em alerta máximo.")
        elif danger == 3:
            lines.append(f"Setor atual: {name}. Risco moderado, mas não subestime o ambiente.")
        else:
            lines.append(f"Setor atual: {name}. Condições relativamente estáveis para operações de rotina.")

    # 3) Perfil do piloto
    if profile:
        xp = profile.get("xp", 0)
        rank = profile.get("rank", "Cadete")

        if xp < 20:
            lines.append(f"A jornada está apenas começando, {rank}. Cada missão conta para sua evolução.")
        elif xp < 100:
            lines.append(f"Bom progresso até aqui. Continue acumulando experiência para novos patamares de comando.")
        else:
            lines.append(f"Seu histórico impressiona. Poucos pilotos alcançam esse nível de experiência.")

    # 4) Inventário
    if inventory:
        rare_items = [
            item for item in inventory
            if isinstance(item, dict) and item.get("rarity") == "rare"
        ]
        if rare_items:
            lines.append("Detectei módulos raros no hangar. Eles podem ser decisivos em situações de risco elevado.")

    # 5) Memória da IA
    memories = get_ai_memory(user_id, limit=1)
    if memories:
        last_memory, last_ts = memories[0]
        lines.append(f"Registro recente na memória da IA: \"{last_memory}\".")

    if not lines:
        lines.append("Nenhuma anomalia detectada. Sistemas estáveis e prontos para a próxima decisão, piloto.")

    return lines[:4]
