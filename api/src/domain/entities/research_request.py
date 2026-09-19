from dataclasses import dataclass
from domain.value_objects.thread_id import ThreadId

@dataclass
class ResearchRequest:
    industry: str
    thread_id: ThreadId
