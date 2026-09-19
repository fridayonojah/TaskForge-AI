from abc import ABC, abstractmethod
from domain.entities.slide_request import SlideRequest
from domain.entities.slide_deck import SlideDeck

class SlideCreator(ABC):
    @abstractmethod
    async def create(self, request: SlideRequest) -> SlideDeck: ...
