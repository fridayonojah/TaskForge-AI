from dataclasses import dataclass, field
from domain.value_objects.thread_id import ThreadId

@dataclass
class ResumeResult:
    original: str
    polished: str
    improvements: list[str]
    thread_id: ThreadId
