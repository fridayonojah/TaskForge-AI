from abc import ABC, abstractmethod
from domain.entities.travel_request import TravelRequest
from domain.entities.travel_plan import TravelPlan


class TravelPlanner(ABC):
    @abstractmethod
    async def plan(self, request: TravelRequest) -> TravelPlan: ...
