from abc import ABC, abstractmethod
from api.src.domain.entities.slide_request import SlideRequest
from api.src.domain.entities.slide_deck import SlideDeck

class SlideCreator(ABC):
    @abstractmethod
    async def create(self, request: SlideRequest) -> SlideDeck: ...
