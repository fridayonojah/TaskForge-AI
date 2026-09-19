from __future__ import annotations
import os
import re
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine


def _async_url(raw: str) -> str:
    url = raw.strip()
    # Normalize scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    # Remove existing driver suffix so we can set asyncpg
    url = re.sub(r"\+(asyncpg|psycopg2|psycopg)", "", url)
    # Set asyncpg driver
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Strip sslmode query param — asyncpg handles SSL via connect_args instead
    url = re.sub(r"[?&]sslmode=\w+", "", url)
    return url


def create_engine() -> AsyncEngine:
    raw = os.environ["DATABASE_URL"]
    url = _async_url(raw)
    return create_async_engine(
        url,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
        echo=os.environ.get("SQL_ECHO", "false").lower() == "true",
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
