MISSIONS_CATALOG = [
    {
        "code": "TRACK_ISS_5MIN",
        "name": "Rastrear a ISS por 5 minutos",
        "description": "Mantenha a nave acompanhando a ISS continuamente por 5 minutos.",
        "xp_reward": 150
    },
    {
        "code": "RUN_SIMPLE_DV",
        "name": "Executar uma manobra de Δv simples",
        "description": "Calcule e execute uma manobra de Δv usando o módulo de manobras.",
        "xp_reward": 100
    },
    {
        "code": "SCAN_RADIATION",
        "name": "Analisar radiação",
        "description": "Realize uma leitura de radiação no módulo de ciência.",
        "xp_reward": 120
    },
    {
        "code": "RADAR_SWEEP",
        "name": "Completar uma varredura de radar",
        "description": "Execute uma varredura completa com o radar da nave.",
        "xp_reward": 130
    }
]

def get_mission_by_code(code: str):
    for m in MISSIONS_CATALOG:
        if m["code"] == code:
            return m
    return None
