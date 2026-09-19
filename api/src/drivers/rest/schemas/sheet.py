from pydantic import BaseModel

from api.src.domain.entities.sheet_request import SheetRequest
from api.src.domain.value_objects.thread_id import ThreadId


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
