import uuid
from datetime import datetime
import json

from fastapi import Depends, HTTPException
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import String, Boolean, TIMESTAMP, func, JSON, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from src.users.models import role, user, company
from src.database.db_client import Base, get_async_session, redis_client
from src.users.schemas import UserRead, CompanyRead
from src.users.utils import similarity_check

"""----------------------------------------------------TABLES--------------------------------------------------------------------------"""


class Company(Base):
    __tablename__ = "company"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    contacts: Mapped[json] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    register_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=func.now(), nullable=False)

# class Product(Base):
#     is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # False - on showing


"""----------------------------------------------------FUNCTIONS--------------------------------------------------------------------------"""


async def get_company_by_id(company_id: str, session: AsyncSession) -> CompanyRead:
    redis_key = f"company:{company_id}"
    cached_company = await redis_client.get(redis_key)
    if cached_company:
        company_data = json.loads(cached_company)
        return CompanyRead(
            id=company_data["id"],
            email=company_data["email"],
            name=company_data["name"],
            description=company_data["description"],
            address=company_data["address"],
            contacts=company_data["contacts"],
            register_at=company_data["register_at"],
        )

    result = await session.execute(
        select(role).where(role.c.id == company_id)
    )
    company_data = result.fetchone()
    if not company_data:
        raise HTTPException(status_code=404, detail=f"Role with id {company_id} not found.")

    answer = {
        "id": company_data[0],
        "email": company_data[1],
        "name": company_data[2],
        "description": company_data[3],
        "address": company_data[4],
        "contacts": company_data[5],
        "register_at": company_data[7],
    }

    await redis_client.setex(redis_key, 86400, json.dumps(answer))

    return CompanyRead(
            id = company_data[0],
            email = company_data[1],
            name = company_data[2],
            description = company_data[3],
            address = company_data[4],
            contacts = company_data[5],
            register_at = company_data[7],
        )