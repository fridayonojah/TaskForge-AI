from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId

@dataclass
class SheetResult:
    topic: str
    csv_content: str
    summary: str
    thread_id: ThreadId
