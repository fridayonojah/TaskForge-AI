from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId

@dataclass
class SheetRequest:
    topic: str
    requirements: str
    thread_id: ThreadId
