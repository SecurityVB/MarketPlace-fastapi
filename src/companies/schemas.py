import uuid
from contextlib import nullcontext
from datetime import datetime

from fastapi_users import schemas
from typing import Any, Dict, Optional
from pydantic import EmailStr, Field, BaseModel



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
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default=None, min_length=5, max_length=50, pattern=r"^[A-Za-z0-9_]+$")
    description: Optional[str] = None
    address: Optional[str] = None
    contacts: Optional[Dict[str, Any]] = None