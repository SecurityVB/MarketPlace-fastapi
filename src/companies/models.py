import uuid

from sqlalchemy import Table, Column, MetaData, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean, func
from sqlalchemy.dialects.postgresql import UUID

company_metadata = MetaData()


company = Table(
    "company",
    company_metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String(length=320), unique=True, index=True, nullable=False),
    Column("name", String(length=50), nullable=False, unique=True),
    Column("description", String, nullable=False),
    Column("address", String, nullable=False),
    Column("contacts", JSON, nullable=False),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("register_at", TIMESTAMP, server_default=func.now(), nullable=False),
)
