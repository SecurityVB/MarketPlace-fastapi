import uuid

from fastapi_users import schemas
from typing import Optional
from pydantic import EmailStr, Field


class UserRead(schemas.BaseUser[str]):
    id: str
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: int
    company_id: Optional[str] = None
    is_verified: Optional[bool] = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    username: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str
    role_id: int
    company_id: str
    first_name: str = Field(max_length=30, pattern=r"^[A-Za-z]+$")
    last_name: str = Field(max_length=30, pattern=r"^[A-Za-z]+$")