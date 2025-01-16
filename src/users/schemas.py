import uuid
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
    username: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-z0-9_]+$")
    email: EmailStr
    password: str
    role_id: int
    company_id: uuid.UUID
    first_name: str = Field(max_length=30, pattern=r"^[A-Za-z]+$")
    last_name: str = Field(max_length=30, pattern=r"^[A-Za-z]+$")

"""----------------------------------COMPANY---------------------------------------"""

class CompanyCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=5, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    description: str
    address: str
    contacts: Dict[str, Any]


class CompanyRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    description: str
    address: str
    contacts: Dict[str, Any]
    register_at: datetime


class CompanyUpdate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=5, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    description: str
    address: str
    contacts: Dict[str, Any]