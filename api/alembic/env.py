from __future__ import annotations
import asyncio
import os
import re
import sys
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from api.alembic import context

# add src/ to path so models import works
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infrastructure.models import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _async_url() -> str:
    raw = os.environ.get(
        "DATABASE_URL",
        "postgresql://taskforge:taskforge123@localhost:5432/taskforge",
    )
    raw = re.sub(r"\+(asyncpg|psycopg2|psycopg)", "", raw)
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql://", 1)
    if not raw.startswith("postgresql+asyncpg://"):
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    raw = re.sub(r"[?&]sslmode=\w+", "", raw)
    return raw


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(_async_url())
    async with engine.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await engine.dispose()


def run_migrations_offline() -> None:
    context.configure(
        url=_async_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
