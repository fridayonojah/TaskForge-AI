from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from drivers.rest.dependencies import get_build_sheet_use_case
from domain.entities.sheet_request import SheetRequest
from domain.value_objects.thread_id import ThreadId
from use_cases.build_sheet_use_case import BuildSheetUseCase

router = APIRouter()


class SheetRequestSchema(BaseModel):
    topic: str
    requirements: str = ""
    thread_id: str | None = None

    def to_entity(self) -> SheetRequest:
        return SheetRequest(
            topic=self.topic,
            requirements=self.requirements,
            thread_id=ThreadId.from_optional(self.thread_id),
        )


class SheetResultSchema(BaseModel):
    success: bool
    topic: str
    csv_content: str
    summary: str
    thread_id: str


@router.post("/sheet", response_model=SheetResultSchema)
async def build_sheet(
    body: SheetRequestSchema,
    use_case: Annotated[BuildSheetUseCase, Depends(get_build_sheet_use_case)],
) -> SheetResultSchema:
    result = await use_case(body.to_entity())
    return SheetResultSchema(
        success=True,
        topic=result.topic,
        csv_content=result.csv_content,
        summary=result.summary,
        thread_id=result.thread_id.value,
    )
