import os
import json
import google.generativeai as genai

from src.api.astronomy import (
    get_celestial_object_by_name,
    record_observation,
    get_observed_object_ids
)
from src.api.telemetry import get_all_telemetry
from src.telemetry.analyzer import compute_stats
from src.missions.mission_definitions import MISSIONS_CATALOG, get_mission_by_code
from src.missions.mission_engine import list_user_missions, complete_mission, assign_mission
from src.api.ai_memory import get_ai_memory
from src.api.logs import add_log

class ShipAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_telemetry_summary(self) -> str:
        """
        Retorna o resumo atual de telemetria da nave (altitude média e velocidade média).
        Use isso se o piloto perguntar como estão a altitude, velocidade ou parâmetros de voo gerais.
        """
        try:
            telemetry_rows = get_all_telemetry(self.user_id)
            stats = compute_stats(telemetry_rows)
            return json.dumps({
                "status": "success",
                "altitude_media_km": stats.get("avg_altitude", 0),
                "velocidade_media_km_h": stats.get("avg_velocity", 0),
                "total_pontos_coletados": stats.get("total_points", 0)
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def search_celestial_catalog(self, name: str) -> str:
        """
        Busca informações científicas detalhadas de um planeta ou estrela no catálogo da nave pelo nome.
        Por exemplo: Sirius, Sol, Canopus, Vega, Betelgeuse, etc.
        """
        try:
            obj = get_celestial_object_by_name(name)
            if not obj:
                return json.dumps({"status": "error", "message": f"Objeto '{name}' não encontrado no catálogo stelar."}, ensure_ascii=False)
            
            observed_ids = get_observed_object_ids(self.user_id)
            is_observed = obj["id"] in observed_ids

            return json.dumps({
                "status": "success",
                "nome": obj["name"],
                "tipo": obj["type"],
                "constelacao": obj["constellation"],
                "distancia_anos_luz": obj["distance_ly"],
                "magnitude_aparente": obj["magnitude"],
                "descricao": obj["description"],
                "ja_observado_pelo_piloto": is_observed
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def record_astronomical_observation(self, name: str) -> str:
        """
        Registra uma observação científica de um planeta ou estrela pelo nome no diário de bordo.
        Recompensa o piloto com +50 XP. Use quando o piloto pedir para observar, registrar ou marcar como visto algum astro.
        """
        try:
            obj = get_celestial_object_by_name(name)
            if not obj:
                return json.dumps({"status": "error", "message": f"Astro '{name}' não encontrado no catálogo para observação."}, ensure_ascii=False)
            
            success = record_observation(self.user_id, obj["id"])
            if success:
                return json.dumps({
                    "status": "success",
                    "message": f"Astro '{obj['name']}' registrado com sucesso no diário! Piloto recebeu +50 XP."
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "warning",
                    "message": f"Astro '{obj['name']}' já havia sido observado anteriormente no diário de bordo."
                }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def list_active_missions(self) -> str:
        """
        Lista todas as missões espaciais que o piloto aceitou e estão em progresso no painel atual.
        """
        try:
            missions = list_user_missions(self.user_id)
            return json.dumps({
                "status": "success",
                "missoes_ativas": missions
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def accept_new_mission(self, code: str) -> str:
        """
        Aceita e inicia uma nova missão do catálogo usando seu código identificador.
        Códigos válidos: TRACK_ISS_5MIN (Rastrear ISS), RUN_SIMPLE_DV (Manobra DeltaV), SCAN_RADIATION (Analisar radiação), RADAR_SWEEP (Varredura de radar).
        """
        try:
            # Lista de missões disponíveis
            valid_codes = [m["code"] for m in MISSIONS_CATALOG]
            if code not in valid_codes:
                catalog_list = [{"code": m["code"], "name": m["name"]} for m in MISSIONS_CATALOG]
                return json.dumps({
                    "status": "error",
                    "message": f"Código de missão inválido: {code}.",
                    "missoes_disponiveis_catalogo": catalog_list
                }, ensure_ascii=False)

            active_missions = list_user_missions(self.user_id)
            # Verifica se já está ativa
            mission_def = get_mission_by_code(code)
            if any(am["name"] == mission_def["name"] for am in active_missions):
                return json.dumps({
                    "status": "warning",
                    "message": f"A missão '{mission_def['name']}' ({code}) já está ativa e em andamento."
                }, ensure_ascii=False)

            res = assign_mission(self.user_id, code)
            if res:
                add_log(self.user_id, f"Missão de treino '{code}' aceita via Assistente IA.", "info")
                return json.dumps({
                    "status": "success",
                    "message": f"Missão '{res['name']}' iniciada com sucesso! Recompensa ao completar: {res['xp_reward']} XP."
                }, ensure_ascii=False)
            return json.dumps({"status": "error", "message": "Falha interna ao aceitar a missão."})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def complete_active_mission(self, code: str) -> str:
        """
        Simula a conclusão e recebe a recompensa de XP de uma missão ativa no diário de bordo usando o seu código.
        Códigos válidos: TRACK_ISS_5MIN, RUN_SIMPLE_DV, SCAN_RADIATION, RADAR_SWEEP.
        """
        try:
            mission_def = get_mission_by_code(code)
            if not mission_def:
                return json.dumps({"status": "error", "message": f"Código de missão inválido: {code}."}, ensure_ascii=False)

            active_missions = list_user_missions(self.user_id)
            target = None
            for am in active_missions:
                if am["name"] == mission_def["name"] and am["status"] == "active":
                    target = am
                    break
            
            if not target:
                return json.dumps({
                    "status": "error",
                    "message": f"A missão '{mission_def['name']}' ({code}) não está ativa no seu diário para ser concluída."
                }, ensure_ascii=False)

            res = complete_mission(self.user_id, target["id"], code)
            if res:
                add_log(self.user_id, f"Missão '{code}' concluída via Assistente IA.", "info")
                return json.dumps({
                    "status": "success",
                    "message": f"Parabéns! Missão '{mission_def['name']}' concluída. Recompensa de +{mission_def['xp_reward']} XP adicionada ao perfil."
                }, ensure_ascii=False)
            return json.dumps({"status": "error", "message": "Falha ao completar a missão."})
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})


def run_offline_fallback(user_message: str, user_id: int) -> str:
    """
    Regras de fallback offline simples para quando o Gemini API Key não estiver configurado.
    """
    msg_lower = user_message.lower()
    
    # 1) Astros
    if "estrela" in msg_lower or "stars" in msg_lower or "sol" in msg_lower or "sirius" in msg_lower or "vega" in msg_lower or "betelgeuse" in msg_lower:
        return ("Estrelas produzem energia através da fusão nuclear. No mapa 3D, temos Sirius (azul-branca), "
                "Canopus, Vega e a supergigante vermelha Betelgeuse. (Modo de Simulação Offline)")
    
    # 2) Planetas
    elif "planeta" in msg_lower or "planets" in msg_lower or "terra" in msg_lower or "marte" in msg_lower:
        return ("Planetas orbitam estrelas. Nosso Sistema Solar possui 8 planetas oficiais. O Sol está no centro (0,0,0) "
                "do nosso mapa 3D. (Modo de Simulação Offline)")
    
    # 3) Telemetria / ISS
    elif "iss" in msg_lower or "estação" in msg_lower or "altitude" in msg_lower or "velocidade" in msg_lower:
        try:
            telemetry_rows = get_all_telemetry(user_id)
            stats = compute_stats(telemetry_rows)
            return (f"A altitude média atual da nave é {stats.get('avg_altitude', 0)} km e a velocidade "
                    f"é {stats.get('avg_velocity', 0)} km/h. (Modo de Simulação Offline)")
        except:
            return "A Estação Espacial Internacional (ISS) está a cerca de 408 km de altitude e viaja a 27.600 km/h. (Modo de Simulação Offline)"
            
    # 4) Missões
    elif "miss" in msg_lower or "militar" in msg_lower or "treino" in msg_lower:
        try:
            missions = list_user_missions(user_id)
            if missions:
                fmt_missions = ", ".join([f"{m['name']} ({m['progress']}% em progresso)" for m in missions])
                return f"Suas missões em andamento: {fmt_missions}. (Modo de Simulação Offline)"
            return "Nenhuma missão ativa no momento. Vá ao menu 'Missões Acadêmicas' para iniciar. (Modo de Simulação Offline)"
        except:
            return "Você pode iniciar missões de treinamento no painel lateral de missões. (Modo de Simulação Offline)"
            
    else:
        return "Entendido, piloto. Sistemas nominalmente estáveis. (Para habilitar o Co-Piloto Inteligente completo, configure a GEMINI_API_KEY no arquivo .env)"


def run_gemini_agent(user_message: str, user_id: int) -> str:
    """
    Executa o agente Gemini inteligente integrado com Function Calling (Tools) e histórico de conversas.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key.strip() in ("", "YOUR_GEMINI_API_KEY"):
        return run_offline_fallback(user_message, user_id)

    try:
        # Configura o cliente do Generative AI
        genai.configure(api_key=api_key)
        
        # Cria a instância da classe que contém as ferramentas (closures/methods com user_id)
        agent_tools = ShipAgent(user_id)
        
        # Define as ferramentas Python expostas ao Gemini
        tools = [
            agent_tools.get_telemetry_summary,
            agent_tools.search_celestial_catalog,
            agent_tools.record_astronomical_observation,
            agent_tools.list_active_missions,
            agent_tools.accept_new_mission,
            agent_tools.complete_active_mission
        ]

        # Configura o modelo com instruções de sistema e as tools registradas
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=(
                "Você é o Agente Co-Piloto Científico inteligente do Cockpit da Nave Planetária.\n"
                "Seu papel é interagir com o piloto humano, auxiliando-o a consultar e gerenciar os sistemas de voo.\n"
                "Use as ferramentas disponíveis para:\n"
                "1. Obter resumos de telemetria de voo.\n"
                "2. Buscar informações detalhadas de planetas/estrelas no catálogo.\n"
                "3. Registrar observações de astros no diário de bordo (dando XP).\n"
                "4. Consultar, iniciar ou concluir missões de treinamento do piloto.\n\n"
                "Instruções Importantes:\n"
                "- Sempre responda em Português.\n"
                "- Seja prestativo, preciso, profissional e mantenha o tom de ficção científica de bordo.\n"
                "- Se o piloto pedir para observar um astro, consulte o catálogo primeiro para confirmar o nome e então chame a ferramenta de registrar observação.\n"
                "- Se o piloto pedir para aceitar ou concluir uma missão, chame as ferramentas de missões adequadas.\n"
                "- Nunca invente informações de telemetria ou missões se as ferramentas puderem fornecê-las."
            ),
            tools=tools
        )

        # Recupera histórico recente de chat gravado no banco de dados para manter o contexto
        memories = get_ai_memory(user_id, limit=6)
        memories.reverse() # Ordena cronologicamente

        # Constrói o histórico formatado para o prompt
        history_context = ""
        if memories:
            history_context = "Histórico de comunicações recentes no Cockpit:\n"
            for mem_text, _ in memories:
                history_context += f"{mem_text}\n"
            history_context += "\n"

        # Executa a sessão de chat inteligente com chamada automática de funções
        chat = model.start_chat(enable_automatic_function_calling=True)
        
        full_prompt = f"{history_context}Piloto atual diz: {user_message}"
        response = chat.send_message(full_prompt)
        
        return response.text.strip()

    except Exception as e:
        print(f"Erro na execução do Agente Gemini: {e}. Usando fallback offline.")
        return run_offline_fallback(user_message, user_id)
