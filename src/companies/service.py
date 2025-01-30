from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import current_user
from src.companies.models import company
from src.companies.schemas import CompanyCreate, CompanyUpdate, CompanyRead
from src.users.database import get_session, User
from src.companies.database import Company


company_router = APIRouter()

@company_router.post("/companies/create", name="create_company")
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


@company_router.post("/companies/update", name="update_company")
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
        answer = (
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
        id=company_answer[0],
        email=company_answer[1],
        name=company_answer[2],
        description=company_answer[3],
        address=company_answer[4],
        contacts=company_answer[5],
        register_at=company_answer[6],
    )