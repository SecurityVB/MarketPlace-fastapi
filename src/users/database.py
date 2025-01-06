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

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(length=20), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    first_name: Mapped[str] = mapped_column(String(length=30))
    last_name: Mapped[str] = mapped_column(String(length=30))
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey(role.c.id))
    company_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey(company.c.id))
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
    company_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey(user.c.id))
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), nullable=False)


class Company(Base):
    __tablename__ = "company"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    contacts: Mapped[json] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), nullable=False)

# class Product(Base):
#     is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # False - on showing


"""----------------------------------------------------FUNCTIONS--------------------------------------------------------------------------"""


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_session(session: AsyncSession = Depends(get_async_session)) -> AsyncSession:
    return session


async def get_users_and_companies(current_row: str, session: AsyncSession) -> UserRead or None:
    users, companies = {}, {}
    users_weights, companies_weights = {}, {}

    result = await session.execute(select(user))
    user_data = result.fetchall()
    result = await session.execute(select(company))
    companies_data = result.fetchall()

    """
    Algorithm for checking differences between a company name or username and the current string
    """

    # for user
    for n in user_data:
        users[n[2]] = n
    for u in users:
        key = u[2]
        row = key.lower().replace(' ', '')
        print(row)
        print(current_row + "\n\n\n")
        table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

        for s in range(1, len(current_row) + 1):
            for c in range(1, len(row) + 1):
                if row[c - 1] == current_row[s - 1]:
                    table[s][c] = table[s - 1][c - 1] + 1
                else:
                    table[s][c] = max(table[s - 1][c], table[s][c - 1])

        for current_row in table:
            print(current_row)

        users_weights[key] = table[-1][-1]

    un = round(len(users) * 0.25)  # How much need return
    sorted_users = sorted(users.keys(), key=lambda tag: users_weights[tag], reverse=True)
    users_answer = {tag: users[tag] for tag in sorted_users[:un]}

    # for company
    if companies:
        for n in companies_data:
            companies[n[2]] = n
        for c in companies:
            key = c[1]
            row = key.lower().replace(' ', '')
            table = [[0 for _ in range(len(row) + 1)] for _ in range(len(current_row) + 1)]

            for s in range(1, len(current_row) + 1):
                for c in range(1, len(row) + 1):
                    if row[c - 1] == current_row[s - 1]:
                        table[s][c] = table[s - 1][c - 1] + 1
                    else:
                        table[s][c] = max(table[s - 1][c], table[s][c - 1])

            for current_row in table:
                print(current_row)

            companies_weights[key] = table[-1][-1]

        cn = round(len(companies) * 0.25) # How much need return
        sorted_companies = sorted(companies.keys(), key=lambda tag: companies_weights[tag], reverse=True)
        companies_answer = {tag: companies[tag] for tag in sorted_companies[:cn]}
    else:
        companies_answer = None

    return {
        "users": users_answer,
        "companies": companies_answer,
    }


async def get_user_by_username(username: str, session: AsyncSession) -> UserRead or None:
    result = await session.execute(
        select(user).where(user.c.username == username)
    )
    user_data = result.fetchone()

    if not user_data:
        return None
    else:
        return UserRead(
            id=user_data[0],
            email=user_data[1],
            username=user_data[2],
            first_name=user_data[4],
            last_name=user_data[5],
            role_id=user_data[7],
            company_id=user_data[8],
            is_verified=user_data[11],
            register_at=user_data[-1],
        )



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
    else:
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