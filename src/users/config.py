import uuid
from fastapi_users import FastAPIUsers

from src.users.auth import auth_backend
from src.users.manager import get_user_manager
from src.users.database import User


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()