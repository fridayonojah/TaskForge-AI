from api.src.domain.entities.sheet_request import SheetRequest
from api.src.domain.entities.sheet_result import SheetResult
from api.src.ports.planners.sheet_builder import SheetBuilder
from api.src.use_cases.exceptions import EmptyQueryError, PlanningFailedError

class BuildSheetUseCase:
    def __init__(self, builder: SheetBuilder) -> None:
        self._builder = builder

    async def __call__(self, request: SheetRequest) -> SheetResult:
        if not request.topic.strip():
            raise EmptyQueryError("Sheet topic cannot be empty")
        try:
            return await self._builder.build(request)
        except (EmptyQueryError, PlanningFailedError):
            raise
        except Exception as exc:
            raise PlanningFailedError(str(exc)) from exc
