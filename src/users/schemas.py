import uuid
from contextlib import nullcontext
from datetime import datetime

from fastapi_users import schemas
from typing import Any, Dict, Optional
from pydantic import EmailStr, Field, BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: int
    company_id: Optional[uuid.UUID] = None
    is_verified: Optional[bool] = False
    register_at: datetime

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = Field(default=None, min_length=5, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    company_id: Optional[uuid.UUID] = None
    first_name: Optional[str] = Field(default=None, max_length=30, pattern=r"^[A-Za-z]+$")
    last_name: Optional[str] = Field(default=None, max_length=30, pattern=r"^[A-Za-z]+$")



class ComplaintCreate(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    company_id: uuid.UUID
    register_at: datetime