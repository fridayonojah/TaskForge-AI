from domain.entities.travel_request import TravelRequest
from domain.entities.travel_plan import TravelPlan
from ports.planners.travel_planner import TravelPlanner
from use_cases.exceptions import EmptyQueryError, PlanningFailedError


class PlanTripUseCase:
    def __init__(self, planner: TravelPlanner) -> None:
        self._planner = planner

    async def __call__(self, request: TravelRequest) -> TravelPlan:
        if not request.query.strip():
            raise EmptyQueryError("Travel query cannot be empty")
        try:
            return await self._planner.plan(request)
        except (EmptyQueryError, PlanningFailedError):
            raise
        except Exception as exc:
            raise PlanningFailedError(str(exc)) from exc
