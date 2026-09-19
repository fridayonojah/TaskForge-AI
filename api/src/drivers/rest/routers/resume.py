from typing import Annotated
from fastapi import APIRouter, Depends

from api.src.drivers.rest.dependencies import get_polish_resume_use_case
from api.src.drivers.rest.schemas.resume import ResumeRequestSchema, ResumeResultSchema
from api.src.use_cases.polish_resume_use_case import PolishResumeUseCase

router = APIRouter()


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
