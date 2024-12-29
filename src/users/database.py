import uuid
from datetime import datetime
import json

from fastapi import Depends, HTTPException
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyBaseUserTableUUID
from sqlalchemy import Integer, String, Boolean, ForeignKey, TIMESTAMP, func, JSON, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional

from src.users.models import role, user, company
from src.database.db_client import Base, get_async_session, redis_client
from src.users.schemas import UserRead


"""----------------------------------------------------TABLES--------------------------------------------------------------------------"""


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(length=20), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=30))
    last_name: Mapped[str] = mapped_column(String(length=30))
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey(role.c.id))
    company_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey(company.c.id))
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False) # for banned
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class Role(Base):  # beginner, verified, seller, owner_by_company
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    permissions: Mapped[json] = mapped_column(JSON)


class Complaint(Base): # on seller / company
    __tablename__ = "complaint"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(length=200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey(user.c.id), nullable=False)
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)


class Company(Base):
    __tablename__ = "company"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    contacts: Mapped[json] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

# class Product(Base):
#     is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # False - on showing


"""----------------------------------------------------FUNCTIONS--------------------------------------------------------------------------"""


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_session(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    return session


async def get_role_by_id(role_id: int, session: AsyncSession) -> dict:
    redis_key = f"role:{role_id}"
    cached_role = await redis_client.get(redis_key)
    if cached_role:
        role_data = json.loads(cached_role)
        return {
            "id": role_data["id"],
            "name": role_data["name"],
            "permissions": role_data["permissions"],
        }

    result = await session.execute(
        select(role).where(role.c.id == role_id)
    )
    role_data = result.fetchone()
    if not role_data:
        raise HTTPException(status_code=404, detail=f"Role with id {role_id} not found")

    role_dict = {"id": role_data[0], "name": role_data[1], "permissions": role_data[2]}
    await redis_client.setex(redis_key, 86400, json.dumps(role_dict))

    return {
        "id": role_dict['id'],
        "name": role_dict['name'],
        "permissions": role_dict['permissions'],
    }


async def get_company_by_id(company_id: str, session: AsyncSession) -> dict:
    redis_key = f"company:{company_id}"
    cached_company = await redis_client.get(redis_key)
    if cached_company:
        company_data = json.loads(cached_company)
        return {
            "id": company_data["id"],
            "name": company_data["name"],
            "description": company_data["description"],
            "address": company_data["address"],
            "contacts": company_data["contacts"],
            "register_at": company_data["register_at"],
        }

    result = await session.execute(
        select(role).where(role.c.id == company_id)
    )
    company_data = result.fetchone()
    if not company_data:
        raise HTTPException(status_code=404, detail=f"Role with id {company_id} not found")

    company_dict = {
        "id": company_data[0],
        "name": company_data[1],
        "description": company_data[2],
        "address": company_data[3],
        "contacts": company_data[4],
        "register_at": company_data[6],
    }

    await redis_client.setex(redis_key, 86400, json.dumps(company_dict))

    return company_dict