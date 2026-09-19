from __future__ import annotations
from datetime import timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.src.domain.entities.user import User
from api.src.domain.value_objects.user_id import UserId
from api.src.infrastructure.models import UserModel
from api.src.ports.repositories.user_repository import UserRepository
from api.src.adapters.exceptions import DatabaseError


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        try:
            result = await self._session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            row = result.scalar_one_or_none()
        except Exception as exc:
            raise DatabaseError(str(exc)) from exc
        if row is None:
            return None
        return self._to_entity(row)

    async def save(self, user: User) -> None:
        model = UserModel(
            id=user.id.value,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DatabaseError(f"User with email {user.email} already exists") from exc
        except Exception as exc:
            await self._session.rollback()
            raise DatabaseError(str(exc)) from exc

    @staticmethod
    def _to_entity(row: UserModel) -> User:
        return User(
            id=UserId(value=row.id),
            email=row.email,
            hashed_password=row.hashed_password,
            is_active=row.is_active,
            created_at=row.created_at,
        )
