from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from drivers.rest.dependencies import get_job_queue
from ports.queue.job_queue import JobQueue

router = APIRouter()


class TravelRequestSchema(BaseModel):
    message: str
    thread_id: str | None = None


class TravelJobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str


@router.post("/travel", response_model=TravelJobResponse)
async def plan_travel(
    body: TravelRequestSchema,
    queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> TravelJobResponse:
    job_id = await queue.enqueue(
        "plan_trip_task",
        {"query": body.message, "thread_id_value": body.thread_id or ""},
    )
    return TravelJobResponse(
        job_id=job_id,
        status="queued",
        message=f"Travel plan queued. Poll GET /api/jobs/{job_id} for results.",
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
