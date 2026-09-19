from abc import ABC, abstractmethod


class HotelSearchTool(ABC):
    @abstractmethod
    def search(self, query: str) -> str: ...
