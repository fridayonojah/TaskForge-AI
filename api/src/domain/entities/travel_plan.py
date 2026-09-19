from dataclasses import dataclass
from api.src.domain.value_objects.thread_id import ThreadId


@dataclass
class TravelPlan:
    thread_id: ThreadId
    answer: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
