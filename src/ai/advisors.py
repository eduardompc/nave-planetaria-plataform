def nav_advisor(telemetry_stats):
    msgs = []

    if telemetry_stats["total_points"] == 0:
        msgs.append("Nenhum dado de voo registrado ainda. Recomendo iniciar uma sessão de navegação.")
    else:
        if telemetry_stats["avg_altitude"] > 410:
            msgs.append("Altitude média acima do nominal. Verifique se a órbita planejada considera esse desvio.")
        if telemetry_stats["avg_velocity"] > 27700:
            msgs.append("Velocidade média elevada. Certifique-se de que não está excedendo o perfil de missão.")

    return msgs

def mission_advisor(active_missions):
    if not active_missions:
        return ["Nenhuma missão ativa. Sugiro aceitar uma nova missão no painel do piloto."]
    
    msgs = ["Você possui missões em andamento. Recomendo priorizar:"]
    for m in active_missions:
        if m["progress"] < 100:
            msgs.append(f"- {m['name']} ({m['progress']}%)")
    return msgs

def systems_advisor(logs_recent):
    if not logs_recent:
        return []

    alerts = [l for l in logs_recent if l["type"] == "alert"]
    warnings = [l for l in logs_recent if l["type"] == "warning"]

    msgs = []
    if alerts:
        msgs.append(f"Atenção: {len(alerts)} alerta(s) recente(s) nos sistemas. Verifique o painel de sistemas.")
    if warnings:
        msgs.append(f"Há {len(warnings)} aviso(s) pendente(s). Recomendo revisar os logs.")

    return msgs
