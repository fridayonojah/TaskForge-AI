from abc import ABC, abstractmethod
from api.src.domain.entities.job import Job

class JobQueue(ABC):
    @abstractmethod
    async def enqueue(self, job_type: str, payload: dict) -> str: ...
    @abstractmethod
    async def get_job(self, job_id: str) -> Job | None: ...
