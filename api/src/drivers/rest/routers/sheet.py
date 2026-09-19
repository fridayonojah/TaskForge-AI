from typing import Annotated
from fastapi import APIRouter, Depends

from api.src.drivers.rest.dependencies import get_build_sheet_use_case
from api.src.drivers.rest.schemas.sheet import SheetRequestSchema, SheetResultSchema
from api.src.use_cases.build_sheet_use_case import BuildSheetUseCase

router = APIRouter()


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
