from fastapi import FastAPI

from src.users.auth import auth_backend
from src.users.schemas import UserCreate, UserRead, UserUpdate
from src.users.service import user_router
from src.users.config import fastapi_users

'''----------------------------------------CONFIG-------------------------------------------------'''

app = FastAPI()

app.include_router(user_router, prefix="/users", tags=["users"])


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