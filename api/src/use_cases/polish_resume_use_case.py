from api.src.domain.entities.resume_request import ResumeRequest
from api.src.domain.entities.resume_result import ResumeResult
from api.src.ports.planners.resume_polisher import ResumePolisher
from api.src.use_cases.exceptions import EmptyQueryError, PlanningFailedError

class PolishResumeUseCase:
    def __init__(self, polisher: ResumePolisher) -> None:
        self._polisher = polisher

    async def __call__(self, request: ResumeRequest) -> ResumeResult:
        if not request.resume_text.strip():
            raise EmptyQueryError("Resume text cannot be empty")
        try:
            return await self._polisher.polish(request)
        except (EmptyQueryError, PlanningFailedError):
            raise
        except Exception as exc:
            raise PlanningFailedError(str(exc)) from exc
