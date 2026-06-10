# database/__init__.py
from .db import init_db, register_user, login_user, get_user_count, save_prediction, get_user_predictions

__all__ = [
    "init_db", "register_user", "login_user",
    "get_user_count", "save_prediction", "get_user_predictions"
]
