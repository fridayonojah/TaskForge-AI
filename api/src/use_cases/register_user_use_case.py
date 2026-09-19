from domain.entities.user import User
from domain.value_objects.user_id import UserId
from ports.repositories.user_repository import UserRepository
from use_cases.exceptions import UserAlreadyExistsError

class RegisterUserUseCase:
    def __init__(self, repo: UserRepository, hash_password_fn) -> None:
        self._repo = repo
        self._hash_password = hash_password_fn

    async def __call__(self, email: str, password: str) -> User:
        existing = await self._repo.get_by_email(email)
        if existing:
            raise UserAlreadyExistsError(f"Email {email} is already registered")
        user = User(
            id=UserId.generate(),
            email=email,
            hashed_password=self._hash_password(password),
        )
        await self._repo.save(user)
        return user
