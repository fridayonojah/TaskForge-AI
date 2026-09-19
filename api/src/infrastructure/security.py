from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(data: dict, secret_key: str, expire_minutes: int = 60) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expire_minutes)
    return jwt.encode(payload, secret_key, algorithm=_ALGORITHM)


def decode_token(token: str, secret_key: str) -> dict:
    try:
        return jwt.decode(token, secret_key, algorithms=[_ALGORITHM])
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc
