import uuid

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from typing_extensions import Any
from fastapi import Depends, APIRouter, HTTPException
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.config import current_user
from src.users.models import company
from src.users.schemas import UserRead, CompanyCreate, CompanyUpdate, CompanyRead
from src.users.database import get_session, get_user_db, get_role_by_id, \
    get_company_by_id, get_user_by_username, get_users_and_companies, \
    Company, User

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
        if role_db['name'] == "owner":
            raise HTTPException(status_code=404, detail="Seller or Owner not found")
        company_db = await get_company_by_id(user_db.company_id, session)

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


@user_router.post("/companies/create", name="create_company")
async def create_company(
    company_data: CompanyCreate,
    user_db: User = Depends(current_user),
    session: AsyncSession = Depends(get_session)
):
    if user_db.company_id == None:
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
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Company with this email already exists.")

        user_db.company_id = new_company.id
        user_db.role_id = 2

        return new_company
    else:
        raise HTTPException(status_code=400, detail="you already own the company.")


@user_router.post("/companies/update", name="update_company")
async def update_company(
    company_data: CompanyUpdate,
    user_db: User = Depends(current_user),
    session: AsyncSession = Depends(get_session)
) -> CompanyRead:
    query = await session.execute(
        select(company).where(company.c.id == user_db.company_id)
    )
    company_db = query.fetchone()
    if not company_db:
        HTTPException(status_code=404, detail="You don't own the company")

    try:
        answer = await session.execute(
            update(company)
            .where(company.c.id == user_db.company_id)
            .values(
                email = company_data.email,
                name = company_data.name,
                description = company_data.description,
                address = company_data.address,
                contacts = company_data.contacts,
            )
            .returning(
                company.c.id,
                company.c.email,
                company.c.name,
                company.c.description,
                company.c.address,
                company.c.contacts,
                company.c.register_at,
            )
        )

        result = await session.execute(answer)
        await session.commit()

        company_answer = result.fetchone()
        if not company_answer:
            raise HTTPException(status_code=500, detail="Failed to create message")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CompanyRead(
        id=company_data[0],
        email=company_data[6],
        name=company_data[1],
        description=company_data[7],
        address=company_data[2],
        contacts=company_data[3],
        register_at=company_data[5],
    )