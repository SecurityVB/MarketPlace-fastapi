import uuid

from sqlalchemy import Table, Column, MetaData, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, func
from sqlalchemy.dialects.postgresql import UUID


user_metadata = MetaData()


role = Table(
    "role",
    user_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON),
)


user = Table(
    "user",
    user_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String(length=320), nullable=False),
    Column("username", String(length=20), nullable=False, unique=True),
    Column("hashed_password", String, nullable=False),
    Column("first_name", String(length=30)),
    Column("last_name", String(length=30)),
    Column("balance", Integer, nullable=False, default=0),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("company_id", UUID(as_uuid=True), ForeignKey(company.c.id)),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("register_at", TIMESTAMP, default=func.now()),
)

complaint = Table(
    "complaint",
    user_metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(length=200), nullable=False),
    Column("content",String, nullable=False),
    Column("user_id", UUID(as_uuid=True), ForeignKey(user.c.id)),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("register_at", TIMESTAMP, server_default=func.now(), nullable=False),
)