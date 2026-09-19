from dataclasses import dataclass
from domain.value_objects.thread_id import ThreadId

@dataclass
class ResumeRequest:
    resume_text: str
    job_description: str | None
    thread_id: ThreadId
