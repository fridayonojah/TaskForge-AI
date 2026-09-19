from abc import ABC, abstractmethod
from api.src.domain.entities.sheet_request import SheetRequest
from api.src.domain.entities.sheet_result import SheetResult

class SheetBuilder(ABC):
    @abstractmethod
    async def build(self, request: SheetRequest) -> SheetResult: ...
