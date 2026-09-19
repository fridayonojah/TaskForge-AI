from __future__ import annotations
import os
from functools import lru_cache
from typing import AsyncGenerator

import certifi
import psycopg
import redis.asyncio as aioredis
from fastapi import Request, Depends
from langchain_groq import ChatGroq
from langgraph.checkpoint.postgres import PostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.src.adapters.cache.redis_cache_store import RedisCacheStore
from api.src.adapters.planners.langgraph_industry_researcher import LangGraphIndustryResearcher
from api.src.adapters.planners.langgraph_resume_polisher import LangGraphResumePolisher
from api.src.adapters.planners.langgraph_sheet_builder import LangGraphSheetBuilder
from api.src.adapters.planners.langgraph_slide_creator import LangGraphSlideCreator
from api.src.adapters.planners.langgraph_travel_planner import LangGraphTravelPlanner
from api.src.adapters.queue.arq_job_queue import ArqJobQueue
from api.src.adapters.repositories.postgres_user_repository import PostgresUserRepository
from api.src.adapters.tools.aviationstack_flight_tool import AviationStackFlightTool
from api.src.adapters.tools.tavily_hotel_tool import TavilyHotelTool
from api.src.adapters.tools.tavily_web_search_tool import TavilyWebSearchTool
from api.src.infrastructure.security import hash_password, verify_password
from api.src.ports.cache.cache_store import CacheStore
from api.src.ports.queue.job_queue import JobQueue
from api.src.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from api.src.use_cases.build_sheet_use_case import BuildSheetUseCase
from api.src.use_cases.create_slides_use_case import CreateSlidesUseCase
from api.src.use_cases.plan_trip_use_case import PlanTripUseCase
from api.src.use_cases.polish_resume_use_case import PolishResumeUseCase
from api.src.use_cases.register_user_use_case import RegisterUserUseCase
from api.src.use_cases.research_industry_use_case import ResearchIndustryUseCase


# ── Singletons (process-scoped) ──────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_llm() -> ChatGroq:
    return ChatGroq(model="llama-3.3-70b-versatile", api_key=os.environ["GROQ_API_KEY"])


@lru_cache(maxsize=1)
def _get_sync_checkpointer() -> PostgresSaver:
    db_url = os.environ["DATABASE_URL"]
    # psycopg needs postgresql:// with no +asyncpg suffix
    import re
    db_url = re.sub(r"\+(asyncpg|psycopg2)", "", db_url)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    if "sslmode" not in db_url:
        db_url += "?sslmode=require"
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    conn = psycopg.connect(db_url)
    cp = PostgresSaver(conn)
    cp.setup()
    return cp


@lru_cache(maxsize=1)
def _get_flight_tool() -> AviationStackFlightTool:
    return AviationStackFlightTool(
        api_key=os.environ["AVIATIONSTACK_API_KEY"],
        default_origin=os.environ.get("DEFAULT_ORIGIN_IATA", "DAC"),
    )


@lru_cache(maxsize=1)
def _get_hotel_tool() -> TavilyHotelTool:
    return TavilyHotelTool(api_key=os.environ["TAVILY_API_KEY"])


@lru_cache(maxsize=1)
def _get_web_search_tool() -> TavilyWebSearchTool:
    return TavilyWebSearchTool(api_key=os.environ["TAVILY_API_KEY"])


# ── App-state helpers (request-scoped) ───────────────────────────────────────

def _get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def get_redis(request: Request) -> aioredis.Redis:
    return request.app.state.redis


# ── Database session dependency ───────────────────────────────────────────────

async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    factory: async_sessionmaker[AsyncSession] = _get_session_factory(request)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Use case factories ────────────────────────────────────────────────────────

def get_plan_trip_use_case() -> PlanTripUseCase:
    planner = LangGraphTravelPlanner(
        flight_tool=_get_flight_tool(),
        hotel_tool=_get_hotel_tool(),
        llm=_get_llm(),
        checkpointer=_get_sync_checkpointer(),
    )
    return PlanTripUseCase(planner=planner)


def get_create_slides_use_case() -> CreateSlidesUseCase:
    return CreateSlidesUseCase(creator=LangGraphSlideCreator(llm=_get_llm()))


def get_polish_resume_use_case() -> PolishResumeUseCase:
    return PolishResumeUseCase(polisher=LangGraphResumePolisher(llm=_get_llm()))


def get_build_sheet_use_case() -> BuildSheetUseCase:
    return BuildSheetUseCase(builder=LangGraphSheetBuilder(llm=_get_llm()))


def get_research_industry_use_case() -> ResearchIndustryUseCase:
    return ResearchIndustryUseCase(
        researcher=LangGraphIndustryResearcher(
            llm=_get_llm(), search_tool=_get_web_search_tool()
        )
    )


async def get_register_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        repo=PostgresUserRepository(session=session),
        hash_password_fn=hash_password,
    )


async def get_authenticate_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> AuthenticateUserUseCase:
    return AuthenticateUserUseCase(
        repo=PostgresUserRepository(session=session),
        verify_password_fn=verify_password,
    )


def get_job_queue(request: Request) -> JobQueue:
    return ArqJobQueue(client=get_redis(request))


def get_cache_store(request: Request) -> CacheStore:
    return RedisCacheStore(client=get_redis(request))
