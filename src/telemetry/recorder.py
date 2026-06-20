from src.api.telemetry import save_telemetry
from src.auth.session import get_current_profile
from src.api.navigation import get_iss_position
import random

def record_tick():
    """
    Grava um ponto de telemetria a cada ciclo do intervalo do Dash.
    """
    profile = get_current_profile()
    if not profile:
        return

    user_id = profile["user_id"]

    # Exemplo: usando posição da ISS como base
    lat, lon = get_iss_position()

    # Simulação de altitude e velocidade
    altitude = 408 + random.uniform(-1, 1)  # km
    velocity = 27600 + random.uniform(-50, 50)  # km/h

    save_telemetry(user_id, lat, lon, altitude, velocity)
