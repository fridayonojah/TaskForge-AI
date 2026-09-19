from pydantic import BaseModel
from domain.entities.travel_request import TravelRequest
from domain.value_objects.thread_id import ThreadId


class TravelRequestSchema(BaseModel):
    message: str
    thread_id: str | None = None

    def to_entity(self) -> TravelRequest:
        return TravelRequest(
            query=self.message,
            thread_id=ThreadId.from_optional(self.thread_id),
        )


class TravelPlanSchema(BaseModel):
    success: bool
    thread_id: str
    answer: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int
