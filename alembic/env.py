import sys
import asyncio
from logging.config import fileConfig
from pathlib import Path

# Add project root to path before any local imports (env.py is run as a script by Alembic).
# Parent of fastapi_clean so that "fastapi_clean" is a top-level package.
_root = Path(__file__).resolve().parents[2] # noqa: E402
if str(_root) not in sys.path: # noqa: E402
    sys.path.insert(0, str(_root)) # noqa: E402

from alembic import context # noqa: E402
from sqlalchemy import pool # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine # noqa: E402

from fastapi_clean.core.config import settings # noqa: E402
from fastapi_clean.infrastructure.driven.db.sqlalchemy.models.base import Base  # noqa: E402

# IMPORTANT: import models so Base.metadata is populated

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url.replace("+asyncpg", "")  # offline wants sync url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online_entry() -> None:
    asyncio.run(run_migrations_online())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online_entry()
