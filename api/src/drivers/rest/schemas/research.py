from pydantic import BaseModel

from api.src.domain.entities.research_request import ResearchRequest
from api.src.domain.value_objects.thread_id import ThreadId


class ResearchRequestSchema(BaseModel):
    industry: str
    thread_id: str | None = None

    def to_entity(self) -> ResearchRequest:
        return ResearchRequest(
            industry=self.industry,
            thread_id=ThreadId.from_optional(self.thread_id),
        )
