from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId


@dataclass
class TravelRequest:
    query: str
    thread_id: ThreadId
