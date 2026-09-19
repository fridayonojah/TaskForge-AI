from domain.entities.research_request import ResearchRequest
from domain.entities.research_result import ResearchResult
from ports.planners.industry_researcher import IndustryResearcher
from use_cases.exceptions import EmptyQueryError, PlanningFailedError

class ResearchIndustryUseCase:
    def __init__(self, researcher: IndustryResearcher) -> None:
        self._researcher = researcher

    async def __call__(self, request: ResearchRequest) -> ResearchResult:
        if not request.industry.strip():
            raise EmptyQueryError("Industry name cannot be empty")
        try:
            return await self._researcher.research(request)
        except (EmptyQueryError, PlanningFailedError):
            raise
        except Exception as exc:
            raise PlanningFailedError(str(exc)) from exc
