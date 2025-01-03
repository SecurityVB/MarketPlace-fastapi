import uuid

from fastapi import FastAPI
from fastapi import Depends, APIRouter
from fastapi_users import FastAPIUsers

from src.users.auth import auth_backend
from src.users.manager import get_user_manager
from src.users.schemas import UserCreate, UserRead, UserUpdate
from src.users.database import User
from src.users.service import user_router

'''----------------------------------------CONFIG-------------------------------------------------'''

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/users/jwt",
    tags=["users"],
)


app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"],
)


app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)