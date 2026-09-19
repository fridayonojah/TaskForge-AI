from typing import Annotated
from fastapi import APIRouter, Depends

from api.src.drivers.rest.dependencies import get_job_queue
from api.src.drivers.rest.schemas.travel import TravelRequestSchema, TravelJobResponse, HealthResponse
from api.src.ports.queue.job_queue import JobQueue

router = APIRouter()


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
