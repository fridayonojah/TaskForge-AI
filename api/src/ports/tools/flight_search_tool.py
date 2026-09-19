from abc import ABC, abstractmethod


class FlightSearchTool(ABC):
    @abstractmethod
    def search(self, query: str) -> str: ...
