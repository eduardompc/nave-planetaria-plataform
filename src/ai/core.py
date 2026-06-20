import os
import google.generativeai as genai
from src.telemetry.analyzer import compute_stats
from src.api.telemetry import get_all_telemetry
from src.api.missions import get_active_missions
from src.api.logs import get_recent_logs
from src.auth.session import get_current_profile
from .advisors import nav_advisor, mission_advisor, systems_advisor

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "YOUR_GEMINI_API_KEY"):
        return None
    try:
        genai.configure(api_key=api_key)
        # Retorna o modelo configurado
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Erro ao configurar a API do Gemini: {e}")
        return None

def generate_ai_briefing():
    profile = get_current_profile()
    if not profile:
        return ["Nenhum piloto autenticado. IA em modo de espera."]

    user_id = profile["user_id"]

    # Coleta de dados reais do banco
    telemetry_rows = get_all_telemetry(user_id)
    stats = compute_stats(telemetry_rows)

    missions = get_active_missions(user_id)
    missions_fmt = [
        {"name": m["mission_name"], "progress": m["progress"], "status": m["status"]}
        for m in missions
    ]

    logs_recent = get_recent_logs(user_id, limit=20)
    logs_fmt = [{"message": l["message"], "type": l["type"]} for l in logs_recent]

    # Tenta usar o Gemini para gerar um briefing científico interativo
    model = get_gemini_client()
    if model:
        try:
            prompt = f"""
Você é a IA Co-Piloto Científico da Nave Planetária. Gere um briefing operacional e de telemetria curto, preciso e de tom científico em Português para o piloto atual.
Dados do cockpit:
- Piloto Patente: {profile['rank']}
- Experiência: {profile['xp']} XP
- Telemetria de Vôo: Altitude média {stats['avg_altitude']} km, Velocidade média {stats['avg_velocity']} km/h (Total de {stats['total_points']} pontos registrados)
- Missões Ativas no Painel: {missions_fmt}
- Logs operacionais recentes: {logs_fmt}

INSTRUÇÕES E REGRAS:
1. Retorne de 3 a 4 itens objetivos (bullet points).
2. Não use marcadores de markdown complexos (como asteriscos de negrito excessivos ou títulos). Use apenas traços '-' para a lista.
3. Seja breve e realista no contexto de ficção científica espacial da nave.
4. Mantenha os avisos científicos baseados diretamente nas regras operacionais caso haja desvios (ex: altitude ideal da ISS é em torno de 408km e velocidade ~27600km/h).
            """
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Divide as linhas e remove linhas em branco ou cabeçalhos
            lines = []
            for line in text.split("\n"):
                line_clean = line.strip().lstrip("-*•").strip()
                if line_clean:
                    lines.append(line_clean)
            
            if len(lines) >= 2:
                return lines[:4]
        except Exception as e:
            print(f"Erro ao gerar briefing via Gemini: {e}. Usando fallback offline.")

    # FALLBACK OFFLINE (Regras estáticas de Advisors)
    msgs = []
    msgs.extend(nav_advisor(stats))
    msgs.extend(mission_advisor(missions_fmt))
    msgs.extend(systems_advisor(logs_recent))

    if not msgs:
        msgs.append("Todos os sistemas operando nos parâmetros nominais de segurança.")

    return msgs
