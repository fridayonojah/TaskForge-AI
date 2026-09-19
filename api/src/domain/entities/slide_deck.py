from dataclasses import dataclass
from domain.value_objects.thread_id import ThreadId

@dataclass
class SlideDeck:
    topic: str
    slides_markdown: str
    thread_id: ThreadId
