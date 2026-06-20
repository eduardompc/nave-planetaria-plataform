from flask_login import LoginManager, UserMixin
from src.api.users import get_user_by_id

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return None
    return User(user["id"], user["username"])
