import uuid

from sqlalchemy.exc import IntegrityError
from typing_extensions import Any
from fastapi import Depends, APIRouter, HTTPException
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserRead, CompanyCreate
from src.users.database import get_session, get_user_db, get_role_by_id, \
    get_company_by_id, get_user_by_username, get_users_and_companies, Company

user_router = APIRouter()

@user_router.get("/profile/{username}", name="get_seller_or_owner_profile")
async def get_seller_or_owner_profile(
    username: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    try:
        user_db = await get_user_by_username(username, session)
        if not user_db:
            raise HTTPException(status_code=404, detail="Seller or Owner not found")
        role_db = await get_role_by_id(user_db.role_id, session)
        company_db = await get_company_by_id(user_db.company_id, session) if role_db['name'] == "owner_by_company" else None

    except UserNotExists:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user_db.username,
        "email": user_db.email,
        "first_name": user_db.first_name,
        "last_name": user_db.last_name,
        "role": role_db,
        "company": company_db,
        "is_verified": user_db.is_verified,
        "register_at": user_db.register_at,
    }


@user_router.get("/profiles/search/{current_row}", name="search_profiles")
async def search_profiles(
    current_row: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    answer = await get_users_and_companies(current_row, session)
    if not answer:
        raise HTTPException(status_code=404, detail="Nothing not found")

    return answer


@user_router.post("/companies/", name="search_profiles")
async def search_profiles(
        company_data: CompanyCreate,
        session: AsyncSession = Depends(get_session)
):
    new_company = Company(
        email=company_data.email,
        name=company_data.name,
        description=company_data.description,
        address=company_data.address,
        contacts=company_data.contacts,
    )

    session.add(new_company)

    try:
        await session.commit()
        await session.refresh(new_company)
        return new_company
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Company with this email already exists.")