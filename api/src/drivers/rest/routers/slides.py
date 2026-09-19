from typing import Annotated
from fastapi import APIRouter, Depends

from api.src.drivers.rest.dependencies import get_create_slides_use_case
from api.src.drivers.rest.schemas.slides import SlidesRequestSchema, SlidesDeckSchema
from api.src.use_cases.create_slides_use_case import CreateSlidesUseCase

router = APIRouter()


@router.post("/slides", response_model=SlidesDeckSchema)
async def create_slides(
    body: SlidesRequestSchema,
    use_case: Annotated[CreateSlidesUseCase, Depends(get_create_slides_use_case)],
) -> SlidesDeckSchema:
    deck = await use_case(body.to_entity())
    return SlidesDeckSchema(
        success=True,
        topic=deck.topic,
        slides_markdown=deck.slides_markdown,
        thread_id=deck.thread_id.value,
    )
