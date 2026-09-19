from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from drivers.rest.dependencies import get_polish_resume_use_case
from domain.entities.resume_request import ResumeRequest
from domain.value_objects.thread_id import ThreadId
from use_cases.polish_resume_use_case import PolishResumeUseCase

router = APIRouter()


class ResumeRequestSchema(BaseModel):
    resume_text: str
    job_description: str | None = None
    thread_id: str | None = None

    def to_entity(self) -> ResumeRequest:
        return ResumeRequest(
            resume_text=self.resume_text,
            job_description=self.job_description,
            thread_id=ThreadId.from_optional(self.thread_id),
        )


class ResumeResultSchema(BaseModel):
    success: bool
    polished: str
    improvements: list[str]
    thread_id: str


@router.post("/resume/polish", response_model=ResumeResultSchema)
async def polish_resume(
    body: ResumeRequestSchema,
    use_case: Annotated[PolishResumeUseCase, Depends(get_polish_resume_use_case)],
) -> ResumeResultSchema:
    result = await use_case(body.to_entity())
    return ResumeResultSchema(
        success=True,
        polished=result.polished,
        improvements=result.improvements,
        thread_id=result.thread_id.value,
    )
