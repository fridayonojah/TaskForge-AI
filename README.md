# TaskForge AI

> Forge any output with AI — a production-grade, multi-agent platform that plans trips, builds slides, polishes resumes, generates spreadsheets, and researches industries through a single REST API.

Built with **FastAPI**, **LangGraph**, and **Hexagonal (Ports & Adapters) Architecture** — engineered for a **React** frontend.

---

## Table of Contents

- [What TaskForge AI Does](#what-taskforge-ai-does)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [API Reference](#api-reference)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running with Docker (Recommended)](#running-with-docker-recommended)
  - [Running Locally](#running-locally)
- [Database Migrations](#database-migrations)
- [Background Jobs](#background-jobs)
- [Authentication](#authentication)
- [Frontend Integration (React)](#frontend-integration-react)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Contributing](#contributing)

---

## What TaskForge AI Does

| Agent Feature | How It Works | Response |
|---|---|---|
| **Plan a Trip** | Flight search → Hotel search → Day-by-day itinerary → Full travel plan | Async (poll job) |
| **Create Slides** | Outline → Full slide deck content | Sync |
| **Polish a Resume** | Gap analysis → Rewritten, role-targeted resume | Sync |
| **Build a Sheet** | Schema design → Spreadsheet data generation | Sync |
| **Research an Industry** | Web search → Analysis → Structured report | Async (poll job) |

Each feature is powered by a dedicated **LangGraph multi-agent graph** backed by **Llama 3.3 70B via Groq**.

---

## Architecture Overview

TaskForge AI uses **Hexagonal Architecture** — the domain has zero framework imports. Everything external (databases, LLMs, Redis, APIs) is wired in through ports (interfaces) and adapters (implementations).

```
┌──────────────────────────────────────────────────────────────────┐
│                      React Frontend                              │
│                  (port 3000 → api:8000)                          │
└─────────────────────────────┬────────────────────────────────────┘
                              │ HTTP / JSON
┌─────────────────────────────▼────────────────────────────────────┐
│                   Drivers  (REST Layer)                          │
│   FastAPI routers · Pydantic schemas · JWT middleware            │
│   Rate limiter · Logging middleware · Exception handlers         │
└─────────────────────────────┬────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────┐
│                        Use Cases                                 │
│   PlanTripUseCase · CreateSlidesUseCase · PolishResumeUseCase    │
│   BuildSheetUseCase · ResearchIndustryUseCase                    │
│   RegisterUserUseCase · AuthenticateUserUseCase                  │
└───────────────┬──────────────────────────────────┬──────────────┘
                │ depends on ports                 │
┌───────────────▼──────────┐          ┌────────────▼──────────────┐
│        Domain            │          │          Ports             │
│  Entities (dataclasses)  │          │  ABCs for every boundary   │
│  Value Objects           │          │  TravelPlanner · UserRepo  │
│  (zero imports)          │          │  JobQueue · CacheStore     │
└──────────────────────────┘          └────────────┬──────────────┘
                                                   │ implemented by
┌──────────────────────────────────────────────────▼──────────────┐
│                         Adapters                                 │
│  LangGraphTravelPlanner · LangGraphSlideCreator                  │
│  LangGraphResumePolisher · LangGraphSheetBuilder                 │
│  LangGraphIndustryResearcher                                     │
│  PostgresUserRepository (SQLAlchemy) · ArqJobQueue              │
│  RedisCacheStore · AviationStackFlightTool · TavilyHotelTool    │
└──────────────────────────────────────────────────┬──────────────┘
                                                   │
┌──────────────────────────────────────────────────▼──────────────┐
│                      Infrastructure                              │
│   SQLAlchemy 2.0 async · Alembic · PostgreSQL 16                │
│   Redis 7 · ARQ worker · structlog · OpenTelemetry              │
│   bcrypt / JWT · slowapi rate limiter                           │
└─────────────────────────────────────────────────────────────────┘
```



## Project Structure

```
taskforge/
├── docker-compose.yml              # All 5 services: postgres, redis, api, worker, frontend
│
├── api/                            # Backend — FastAPI application
│   ├── Dockerfile                  # Multi-stage: builder (pip install) + runtime
│   ├── entrypoint.sh               # alembic upgrade head → uvicorn
│   ├── worker_entrypoint.sh        # Starts ARQ background worker
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py                  # Async Alembic configuration
│   │   └── versions/               # Migration files
│   └── src/
│       ├── domain/
│       │   ├── entities/           # TravelRequest, TravelPlan, User, Job, SlideRequest...
│       │   └── value_objects/      # UserId, ThreadId
│       ├── ports/
│       │   ├── planners/           # TravelPlanner, SlideCreator, etc. (ABCs)
│       │   ├── repositories/       # UserRepository (ABC)
│       │   ├── tools/              # FlightSearchTool, HotelSearchTool (ABCs)
│       │   ├── queue/              # JobQueue (ABC)
│       │   └── cache/              # CacheStore (ABC)
│       ├── use_cases/              # One use case per feature; depends only on ports + domain
│       ├── adapters/
│       │   ├── planners/           # LangGraph implementations (one per agent feature)
│       │   ├── repositories/       # PostgresUserRepository
│       │   ├── tools/              # AviationStack + Tavily integrations
│       │   ├── queue/              # ArqJobQueue
│       │   └── cache/              # RedisCacheStore
│       ├── infrastructure/
│       │   ├── database.py         # create_engine(), create_session_factory()
│       │   ├── models.py           # UserModel (SQLAlchemy ORM)
│       │   ├── security.py         # bcrypt hash/verify + JWT create/decode
│       │   ├── logging.py          # structlog JSON configuration
│       │   ├── tracing.py          # OpenTelemetry setup (no-op if OTLP_ENDPOINT unset)
│       │   ├── redis_client.py
│       │   └── worker/
│       │       ├── tasks.py        # plan_trip_task, research_industry_task
│       │       └── settings.py     # ARQ WorkerSettings
│       ├── drivers/
│       │   └── rest/
│       │       ├── main.py         # FastAPI app + lifespan (engine, session factory, redis)
│       │       ├── dependencies.py # Dependency injection for all use cases
│       │       ├── exception_handlers.py
│       │       ├── middleware/
│       │       │   ├── logging_middleware.py    # Injects request_id into every log line
│       │       │   └── rate_limit_middleware.py # slowapi 100 req/min per IP
│       │       └── routers/
│       │           ├── auth.py     # POST /api/auth/register, POST /api/auth/token
│       │           ├── travel.py   # POST /api/travel, GET /api/health
│       │           ├── slides.py   # POST /api/slides
│       │           ├── resume.py   # POST /api/resume
│       │           ├── sheet.py    # POST /api/sheet
│       │           ├── research.py # POST /api/research
│       │           └── jobs.py     # GET /api/jobs/{job_id}
│       └── tests/
│           ├── unit/               # Mocked-port use case tests (no DB required)
│           └── performance/        # Locust load tests (50–100 concurrent users)
│
├── frontend/                       # Replace with your React app
│
└── .github/
    └── workflows/
        └── ci.yml                  # lint → type-check → unit tests → docker build
```

---

## Tech Stack

### Backend

| Concern | Library / Tool |
|---|---|
| API framework | FastAPI 0.136 + Uvicorn |
| AI agents | LangGraph 1.2 · LangChain · ChatGroq (Llama 3.3 70B) |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Database | PostgreSQL 16 |
| Background jobs | Redis 7 + ARQ |
| Auth | python-jose (JWT) · passlib (bcrypt) |
| Rate limiting | slowapi (100 req/min per IP) |
| Structured logging | structlog (JSON + request_id) |
| Distributed tracing | OpenTelemetry SDK + OTLP exporter |
| Retry logic | tenacity (exponential backoff, 3 attempts) |
| Flight data | AviationStack API |
| Hotel + search | Tavily API |
| Code quality | ruff (lint) · mypy (type check) |
| Performance tests | Locust |

### Infrastructure

| Service | Image | Purpose |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | User data + LangGraph checkpoints |
| Redis | `redis:7-alpine` | Job queue + response cache |
| API | Custom `python:3.11-slim` | FastAPI server (2 Uvicorn workers) |
| Worker | Same image, different entrypoint | ARQ background job processor |
| Frontend | Custom (replace with React) | Serves the React app |

---

## API Reference

Full interactive docs available at `http://localhost:8000/docs` when running.

---

### Authentication

#### Register

```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Response `201`:
```json
{ "id": "uuid", "email": "user@example.com" }
```

#### Login

```
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=your_password
```

Response `200`:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

---

### Plan a Trip

```
POST /api/travel
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "Plan a 5-day trip from Dhaka to Bangkok in October",
  "thread_id": "optional-uuid-for-conversation-memory"
}
```

Response `200` (job queued):
```json
{
  "job_id": "abc123",
  "status": "queued",
  "message": "Travel plan queued. Poll GET /api/jobs/abc123 for results."
}
```

---

### Create Slides

```
POST /api/slides
Authorization: Bearer <token>
Content-Type: application/json

{
  "topic": "The Future of Renewable Energy",
  "num_slides": 8,
  "audience": "investors"
}
```

Response `200` (synchronous):
```json
{
  "title": "The Future of Renewable Energy",
  "slides": [
    { "slide_number": 1, "title": "...", "content": "..." },
    ...
  ]
}
```

---

### Polish a Resume

```
POST /api/resume
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_text": "... your current resume ...",
  "target_role": "Senior Backend Engineer",
  "job_description": "... optional JD ..."
}
```

Response `200` (synchronous):
```json
{
  "polished_resume": "...",
  "changes_summary": "..."
}
```

---

### Build a Spreadsheet

```
POST /api/sheet
Authorization: Bearer <token>
Content-Type: application/json

{
  "description": "Monthly SaaS revenue tracker with MRR, churn, and growth columns",
  "rows": 20
}
```

Response `200` (synchronous):
```json
{
  "schema": [...],
  "data": [...]
}
```

---

### Research an Industry

```
POST /api/research
Authorization: Bearer <token>
Content-Type: application/json

{
  "industry": "Electric Vehicles",
  "focus": "market trends and key players in Southeast Asia"
}
```

Response `200` (job queued):
```json
{
  "job_id": "def456",
  "status": "queued",
  "message": "Research queued. Poll GET /api/jobs/def456 for results."
}
```

---

### Poll Job Status

```
GET /api/jobs/{job_id}
Authorization: Bearer <token>
```

Response `200`:
```json
{
  "job_id": "abc123",
  "job_type": "plan_trip_task",
  "status": "complete",
  "result": { ... },
  "error": null
}
```

`status` values: `queued` · `in_progress` · `complete` · `failed`

---

### Health Check

```
GET /api/health
```
```json
{ "status": "ok" }
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- API keys for Groq, AviationStack, and Tavily

### Environment Variables

```bash
cp api/.env.example api/.env
```

Then edit `api/.env`:

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key (Llama 3.3 70B) |
| `AVIATIONSTACK_API_KEY` | Yes | Real flight data |
| `TAVILY_API_KEY` | Yes | Hotel + web search |
| `SECRET_KEY` | Yes | Random 32+ character string for JWT signing |
| `DATABASE_URL` | Auto (Docker) | Overridden to `postgres` hostname in Compose |
| `REDIS_URL` | Auto (Docker) | Overridden to `redis` hostname in Compose |
| `JWT_EXPIRE_MINUTES` | No (default: 60) | Token lifetime in minutes |
| `DEFAULT_ORIGIN_IATA` | No (default: DAC) | Default departure airport code |
| `OTLP_ENDPOINT` | No | OpenTelemetry collector — tracing is a no-op if unset |
| `LOG_LEVEL` | No (default: INFO) | `DEBUG` · `INFO` · `WARNING` |
| `SQL_ECHO` | No (default: false) | Set `true` to log all SQL queries |

---

### Running with Docker (Recommended)

```bash
# 1. Clone
git clone https://github.com/fridayonojah/TaskForge-AI.git
cd TaskForge-AI

# 2. Configure
cp api/.env.example api/.env
# Fill in GROQ_API_KEY, AVIATIONSTACK_API_KEY, TAVILY_API_KEY, SECRET_KEY

# 3. Start everything
docker compose up --build
```

Services start in dependency order (enforced by healthchecks):

```
postgres (healthy)
    └── redis (healthy)
            └── api  →  alembic upgrade head  →  uvicorn starts  (healthy)
                    ├── worker  (starts after api is healthy)
                    └── frontend
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Interactive Docs | http://localhost:8000/docs |
| Frontend | http://localhost:3000 |

---

### Running Locally

```bash
# 1. Start only infrastructure
docker compose up postgres redis -d

# 2. Install dependencies
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure .env (use localhost URLs)
cp .env.example .env
# DATABASE_URL=postgresql://taskforge:taskforge123@localhost:5432/taskforge
# REDIS_URL=redis://localhost:6379/0

# 4. Apply migrations
export PYTHONPATH=src
alembic upgrade head

# 5. Start API
cd src
uvicorn drivers.rest.main:app --reload --port 8000

# 6. Start ARQ worker (separate terminal)
cd api/src
export PYTHONPATH=.
arq infrastructure.worker.settings.WorkerSettings
```

---

## Database Migrations

Migrations live in `api/alembic/versions/` and are managed by **Alembic** with an async SQLAlchemy engine.

```bash
# Apply all migrations (runs automatically on Docker startup)
alembic upgrade head

# Create a new migration after editing infrastructure/models.py
alembic revision --autogenerate -m "add_sessions_table"

# Roll back one step
alembic downgrade -1

# Show current revision
alembic current
```

The `entrypoint.sh` runs `alembic upgrade head` on every container start before Uvicorn accepts traffic, so schema is always current.

---

## Background Jobs

Travel planning and industry research are processed asynchronously via **ARQ** (Redis-backed job queue). Synchronous features (slides, resume, sheet) return results directly.

```
React App                       API Server                    ARQ Worker
    │                               │                               │
    │  POST /api/travel             │                               │
    ├──────────────────────────────▶│                               │
    │  { job_id, status:"queued" }  │  enqueue → Redis              │
    │◀──────────────────────────────├──────────────────────────────▶│
    │                               │                               │  run LangGraph graph
    │  GET /api/jobs/{job_id}       │                               │  store result in Redis
    ├──────────────────────────────▶│                               │
    │  { status:"complete",result } │◀──────────────────────────────│
    │◀──────────────────────────────│                               │
```

**React polling pattern:**
```typescript
const pollJob = async (jobId: string) => {
  const interval = setInterval(async () => {
    const res = await fetch(`/api/jobs/${jobId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const job = await res.json();
    if (job.status === 'complete' || job.status === 'failed') {
      clearInterval(interval);
      setResult(job.result);
    }
  }, 2500);
};
```

---

## Authentication

TaskForge AI uses **JWT Bearer tokens** with bcrypt-hashed passwords. All feature endpoints require a valid token.

**React login flow:**
```typescript
// 1. Login
const res = await fetch('/api/auth/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: new URLSearchParams({ username: email, password }),
});
const { access_token } = await res.json();
localStorage.setItem('token', access_token);

// 2. Use token on every request
const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`,
};

// 3. Plan a trip
const job = await fetch('/api/travel', {
  method: 'POST',
  headers,
  body: JSON.stringify({ message: 'Plan a 7-day trip to Japan' }),
}).then(r => r.json());
```

---

## Frontend Integration (React)

The `frontend/` directory is a placeholder. Replace it with a standard React/Vite project.

### Quick Setup

```bash
cd frontend
npm create vite@latest . -- --template react-ts
npm install
```

### Replace the Dockerfile

```dockerfile
# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

Update the `frontend` service port in `docker-compose.yml` from `3000:3000` to `80:80`.

### Key Integration Points

| Backend Behaviour | React Approach |
|---|---|
| Travel + Research return `job_id` | Poll `GET /api/jobs/{id}` every 2–3 s (React Query or `setInterval`) |
| Slides, Resume, Sheet are synchronous | Single `await fetch(...)` — no polling needed |
| All endpoints require Bearer token | Axios interceptor or a `fetch` wrapper that injects the header |
| `status` can be `queued` / `in_progress` / `complete` / `failed` | Show a spinner until `complete`; show error state on `failed` |
| `thread_id` on travel requests | Persist per-conversation UUID in `localStorage` for multi-turn memory |

---

## Testing

### Unit Tests

Tests mock all ports — no database or Redis required.

```bash
cd api/src
pytest tests/unit/ -v --cov=. --cov-report=html
# Coverage report written to htmlcov/index.html
```

### Performance Tests (Locust)

Validates the API under 50–100 concurrent users.

```bash
# Start the API first, then:
cd api/src
locust -f tests/performance/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089 to launch the test
```

---

## CI/CD

GitHub Actions pipeline defined in `.github/workflows/ci.yml`.

**Triggers:** push to `main` or `develop`; all PRs targeting `main`.

```
┌─────────────────────────────────────────────────────────┐
│  test job  (ubuntu-latest + postgres:16 + redis:7)      │
│                                                         │
│  1. pip install -r requirements.txt                     │
│  2. ruff check src/          (lint — fails build)       │
│  3. mypy src/                (type check — advisory)    │
│  4. pytest tests/unit/ -v    (unit tests + coverage)    │
│  5. Upload coverage → Codecov                           │
└───────────────────────────┬─────────────────────────────┘
                            │ on success
┌───────────────────────────▼─────────────────────────────┐
│  docker-build job                                       │
│                                                         │
│  1. docker build taskforge-api                          │
│  2. docker build taskforge-frontend                     │
└─────────────────────────────────────────────────────────┘
```

---

## Contributing

1. Fork the repo and create a feature branch: `git checkout -b feat/your-feature`
2. Follow the agent feature pattern:
   - Domain entity → `domain/entities/`
   - Port ABC → `ports/planners/`
   - LangGraph adapter → `adapters/planners/`
   - Use case → `use_cases/`
   - Router → `drivers/rest/routers/`
   - Unit test → `tests/unit/`
3. Run `ruff check src/` and `pytest tests/unit/` before pushing
4. Open a PR against `main`

---

## License

MIT
