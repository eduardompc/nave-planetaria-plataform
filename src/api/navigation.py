import requests
import time

# Cache global para evitar travar o servidor single-thread com requisições HTTP frequentes
_cached_pos = (-22.9, -43.2) # Começa no Rio de Janeiro como fallback legal
_last_fetch = 0.0

def get_iss_position():
    """
    Retorna latitude e longitude atuais da ISS usando a API open-notify com cache.
    """
    global _cached_pos, _last_fetch
    now = time.time()
    
    # Se o cache tiver menos de 15 segundos, retorna o valor cacheado imediatamente
    if now - _last_fetch < 15.0:
        return _cached_pos
        
    try:
        url = "http://api.open-notify.org/iss-now.json"
        response = requests.get(url, timeout=1.5) # Timeout menor de 1.5s para evitar gargalo
        data = response.json()

        lat = float(data["iss_position"]["latitude"])
        lon = float(data["iss_position"]["longitude"])

        _cached_pos = (lat, lon)
        _last_fetch = now
        return lat, lon

    except Exception:
        # Retorna o último valor do cache em caso de erro de conexão/timeout
        return _cached_pos

