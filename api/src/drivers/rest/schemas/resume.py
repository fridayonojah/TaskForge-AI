from pydantic import BaseModel

from api.src.domain.entities.resume_request import ResumeRequest
from api.src.domain.value_objects.thread_id import ThreadId


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
