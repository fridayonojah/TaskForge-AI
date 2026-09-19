from abc import ABC, abstractmethod
from domain.entities.resume_request import ResumeRequest
from domain.entities.resume_result import ResumeResult

class ResumePolisher(ABC):
    @abstractmethod
    async def polish(self, request: ResumeRequest) -> ResumeResult: ...
