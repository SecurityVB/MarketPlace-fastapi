from fastapi import Depends, APIRouter, HTTPException
from fastapi_users.exceptions import UserNotExists
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Any

from src.users.database import get_session, get_user_db, get_role_by_id, get_company_by_id
from src.users.schemas import UserRead

user_router = APIRouter()

@user_router.get("/profile/{user_id}", name="get_user_profile")
async def get_user_profile(
    user_id: str,
    session: AsyncSession = Depends(get_session),
    user_db=Depends(get_user_db),
) -> dict[str, Any]:
    try:
        user = await user_db.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        role = await get_role_by_id(user.role_id, session)
        company = await get_company_by_id(user.company_id, session) if role['name'] == "owner_by_company" else None

    except UserNotExists:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "balance": user.balance,
        "role": role,
        "company": company,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }