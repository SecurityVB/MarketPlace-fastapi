import uuid
from typing_extensions import Any
from fastapi import Depends, APIRouter, HTTPException
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import UserRead
from src.users.database import get_session, get_user_db, get_role_by_id, \
    get_company_by_id, get_user_by_username, get_users_and_companies


user_router = APIRouter()

@user_router.get("/profile/{username}", name="get_seller_or_owner_profile")
async def get_seller_or_owner_profile(
    username: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    try:
        user = await get_user_by_username(username, session)
        if not user:
            raise HTTPException(status_code=404, detail="Seller or Owner not found")
        role = await get_role_by_id(user.role_id, session)
        company = await get_company_by_id(user.company_id, session) if role['name'] == "owner_by_company" else None

    except UserNotExists:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role,
        "company": company,
        "is_verified": user.is_verified,
        "register_at": user.register_at,
    }


@user_router.get("/profiles/search/{row}", name="search_profiles")
async def get_seller_or_owner_profile(
    row: str,
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    try:
        answer = await get_users_and_companies(row, session)

    except:
        raise HTTPException(status_code=404, detail="Nothing not found")

    return answer