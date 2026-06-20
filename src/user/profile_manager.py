from src.api.profiles import get_profile, add_xp
from src.user.rank_system import get_rank_from_xp

def get_full_profile(user_id):
    profile = get_profile(user_id)
    if not profile:
        return None

    xp = profile["xp"]
    rank = get_rank_from_xp(xp)

    return {
        "user_id": user_id,
        "rank": rank,
        "xp": xp,
        "theme": profile["theme_preference"],
        "last_login": profile["last_login"] if profile["last_login"] else "Primeiro acesso"
    }

def reward_user(user_id, xp_amount):
    add_xp(user_id, xp_amount)
    return get_full_profile(user_id)
