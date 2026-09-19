from typing import Annotated
from fastapi import APIRouter, Depends

from api.src.drivers.rest.dependencies import get_job_queue
from api.src.drivers.rest.schemas.jobs import JobEnqueuedResponse
from api.src.drivers.rest.schemas.research import ResearchRequestSchema
from api.src.ports.queue.job_queue import JobQueue

router = APIRouter()


@router.post("/research", response_model=JobEnqueuedResponse)
async def research_industry(
    body: ResearchRequestSchema,
    queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobEnqueuedResponse:
    job_id = await queue.enqueue(
        "research_industry_task",
        {"industry": body.industry, "thread_id_value": body.thread_id or ""},
    )
    return JobEnqueuedResponse(
        job_id=job_id,
        status="queued",
        message=f"Research job queued. Poll GET /api/jobs/{job_id} for results.",
    )
