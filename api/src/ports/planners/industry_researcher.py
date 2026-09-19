from abc import ABC, abstractmethod
from api.src.domain.entities.research_request import ResearchRequest
from api.src.domain.entities.research_result import ResearchResult

class IndustryResearcher(ABC):
    @abstractmethod
    async def research(self, request: ResearchRequest) -> ResearchResult: ...
