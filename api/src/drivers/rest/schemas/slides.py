from pydantic import BaseModel

from api.src.domain.entities.slide_request import SlideRequest
from api.src.domain.value_objects.thread_id import ThreadId


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
