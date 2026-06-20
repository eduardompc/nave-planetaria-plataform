from flask_login import current_user
from src.api.profiles import update_last_login
from src.user.profile_manager import get_full_profile

def on_user_login():
    if current_user.is_authenticated:
        update_last_login(current_user.id)

def get_current_profile():
    if not current_user.is_authenticated:
        return None
    return get_full_profile(current_user.id)
