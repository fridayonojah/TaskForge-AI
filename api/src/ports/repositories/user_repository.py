from abc import ABC, abstractmethod
from api.src.domain.entities.user import User

class UserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...
    @abstractmethod
    async def save(self, user: User) -> None: ...
