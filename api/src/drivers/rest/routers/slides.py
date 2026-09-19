from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from drivers.rest.dependencies import get_create_slides_use_case
from domain.entities.slide_request import SlideRequest
from domain.value_objects.thread_id import ThreadId
from use_cases.create_slides_use_case import CreateSlidesUseCase

router = APIRouter()


class SlidesRequestSchema(BaseModel):
    topic: str
    num_slides: int = 8
    thread_id: str | None = None

    def to_entity(self) -> SlideRequest:
        return SlideRequest(
            topic=self.topic,
            num_slides=self.num_slides,
            thread_id=ThreadId.from_optional(self.thread_id),
        )


class SlidesDeckSchema(BaseModel):
    success: bool
    topic: str
    slides_markdown: str
    thread_id: str


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
