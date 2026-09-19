from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from api.src.drivers.rest.dependencies import get_job_queue
from api.src.drivers.rest.schemas.jobs import JobStatusResponse
from api.src.ports.queue.job_queue import JobQueue

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> JobStatusResponse:
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status,
        result=job.result,
        error=job.error,
    )
