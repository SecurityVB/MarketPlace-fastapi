from logging.config import fileConfig
from sqlalchemy import engine_from_config, MetaData
from sqlalchemy import pool
from alembic import context

from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASS
from src.users.models import user_metadata

# Alembic Config
config = context.config

section = config.config_ini_section
config.set_section_option(section, 'DB_HOST', DB_HOST)
config.set_section_option(section, 'DB_PORT', DB_PORT)
config.set_section_option(section, 'DB_USER', DB_USER)
config.set_section_option(section, 'DB_NAME', DB_NAME)
config.set_section_option(section, 'DB_PASS', DB_PASS)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata
metadata = MetaData()
for m in [user_metadata, ]:
    for table in m.tables.values():
        metadata._add_table(table.name, table.schema, table)

target_metadata = metadata

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()