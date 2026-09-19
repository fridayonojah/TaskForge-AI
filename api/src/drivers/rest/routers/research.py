from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from drivers.rest.dependencies import get_research_industry_use_case, get_job_queue
from domain.entities.research_request import ResearchRequest
from domain.value_objects.thread_id import ThreadId
from ports.queue.job_queue import JobQueue
from use_cases.research_industry_use_case import ResearchIndustryUseCase

router = APIRouter()


class ResearchRequestSchema(BaseModel):
    industry: str
    thread_id: str | None = None

    def to_entity(self) -> ResearchRequest:
        return ResearchRequest(
            industry=self.industry,
            thread_id=ThreadId.from_optional(self.thread_id),
        )


class ResearchJobResponse(BaseModel):
    job_id: str
    status: str
    message: str


@router.post("/research", response_model=ResearchJobResponse)
async def research_industry(
    body: ResearchRequestSchema,
    queue: Annotated[JobQueue, Depends(get_job_queue)],
) -> ResearchJobResponse:
    job_id = await queue.enqueue(
        "research_industry_task",
        {"industry": body.industry, "thread_id_value": body.thread_id or ""},
    )
    return ResearchJobResponse(
        job_id=job_id,
        status="queued",
        message=f"Research job queued. Poll GET /api/jobs/{job_id} for results.",
    )
