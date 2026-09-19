from api.src.domain.entities.slide_request import SlideRequest
from api.src.domain.entities.slide_deck import SlideDeck
from api.src.ports.planners.slide_creator import SlideCreator
from api.src.use_cases.exceptions import EmptyQueryError, PlanningFailedError

class CreateSlidesUseCase:
    def __init__(self, creator: SlideCreator) -> None:
        self._creator = creator

    async def __call__(self, request: SlideRequest) -> SlideDeck:
        if not request.topic.strip():
            raise EmptyQueryError("Slide topic cannot be empty")
        try:
            return await self._creator.create(request)
        except (EmptyQueryError, PlanningFailedError):
            raise
        except Exception as exc:
            raise PlanningFailedError(str(exc)) from exc
