from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.src.drivers.rest.exception_handlers import register_exception_handlers
from api.src.drivers.rest.middleware.logging_middleware import LoggingMiddleware
from api.src.drivers.rest.middleware.rate_limit_middleware import limiter
from api.src.drivers.rest.routers.auth import router as auth_router
from api.src.drivers.rest.routers.jobs import router as jobs_router
from api.src.drivers.rest.routers.research import router as research_router
from api.src.drivers.rest.routers.resume import router as resume_router
from api.src.drivers.rest.routers.sheet import router as sheet_router
from api.src.drivers.rest.routers.slides import router as slides_router
from api.src.drivers.rest.routers.travel import router as travel_router
from api.src.infrastructure.database import create_engine, create_session_factory
from api.src.infrastructure.logging import configure_logging
from api.src.infrastructure.redis_client import create_redis_client
from api.src.infrastructure.tracing import configure_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    engine = create_engine()
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    app.state.redis = create_redis_client()
    yield
    await app.state.engine.dispose()
    await app.state.redis.aclose()


app = FastAPI(title="TaskForge AI", version="2.0.0", lifespan=lifespan)

configure_tracing(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/api")
app.include_router(travel_router, prefix="/api")
app.include_router(slides_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(sheet_router, prefix="/api")
app.include_router(research_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
