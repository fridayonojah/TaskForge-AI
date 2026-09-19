from domain.entities.user import User
from ports.repositories.user_repository import UserRepository
from use_cases.exceptions import InvalidCredentialsError

class AuthenticateUserUseCase:
    def __init__(self, repo: UserRepository, verify_password_fn) -> None:
        self._repo = repo
        self._verify_password = verify_password_fn

    async def __call__(self, email: str, password: str) -> User:
        user = await self._repo.get_by_email(email)
        if not user or not self._verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        if not user.is_active:
            raise InvalidCredentialsError("Account is inactive")
        return user
