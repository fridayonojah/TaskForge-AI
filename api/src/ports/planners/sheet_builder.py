from abc import ABC, abstractmethod
from domain.entities.sheet_request import SheetRequest
from domain.entities.sheet_result import SheetResult

class SheetBuilder(ABC):
    @abstractmethod
    async def build(self, request: SheetRequest) -> SheetResult: ...
