from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId

@dataclass
class SlideRequest:
    topic: str
    num_slides: int
    thread_id: ThreadId
