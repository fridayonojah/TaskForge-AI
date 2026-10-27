# TaskForge AI

TaskForge is an AI-powered app for travel planning, industry research, slide creation, resume editing, and spreadsheet generation. It uses a FastAPI backend, LangGraph agents, and a React frontend.

Travel planning and industry research run as background jobs. The other features return results directly. Feature endpoints require a bearer token.

## Run with Docker

Prerequisites: Docker Desktop and API keys for Groq, AviationStack, and Tavily.

```bash
cp api/.env.example api/.env
```

Add your keys to `api/.env` and replace `SECRET_KEY` with a unique random value. Then start the app:

```bash
docker compose up --build
```

Open the frontend at [http://localhost:3000](http://localhost:3000) or the API docs at [http://localhost:8000/docs](http://localhost:8000/docs). Compose starts PostgreSQL, Redis, the API, a background worker, and the frontend.

## Features and API

| Feature | Endpoint | Response |
|---|---|---|
| Register / sign in | `POST /api/auth/register`, `POST /api/auth/token` | User / access token |
| Plan a trip | `POST /api/travel` | Background job |
| Research an industry | `POST /api/research` | Background job |
| Create slides | `POST /api/slides` | Immediate result |
| Polish a resume | `POST /api/resume` | Immediate result |
| Build a spreadsheet | `POST /api/sheet` | Immediate result |
| Check a background job | `GET /api/jobs/{job_id}` | Job status and result |
| Health check | `GET /api/health` | Service status |

Use the access token as `Authorization: Bearer <token>` for protected endpoints. Poll the job endpoint to retrieve travel and research results. Interactive request and response schemas are available at `/docs`.

## Configuration

Set these values in `api/.env`:

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Language model access |
| `AVIATIONSTACK_API_KEY` | Flight search |
| `TAVILY_API_KEY` | Hotel and web search |
| `SECRET_KEY` | JWT signing; use a unique secret |

Docker Compose configures the database and Redis URLs. Optional settings, including logging, tracing, and token lifetime, are listed in `api/.env.example`.

## Development Checks

Run the backend checks from the `api` directory:

```bash
ruff check src/
cd src
pytest tests/unit/ -v
```

Build or lint the frontend from `frontend`:

```bash
npm run build
npm run lint
```

## Project Layout

- `api/src/domain`, `ports`, and `use_cases`: core business logic
- `api/src/adapters` and `infrastructure`: AI providers, database, cache, and job queue
- `api/src/drivers/rest`: FastAPI routes and middleware
- `frontend/src`: React application

Database migrations are managed with Alembic and run automatically when the API container starts.
