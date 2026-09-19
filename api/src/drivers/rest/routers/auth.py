import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.src.drivers.rest.dependencies import get_register_use_case, get_authenticate_use_case
from api.src.drivers.rest.schemas.auth import RegisterRequest, TokenResponse
from api.src.infrastructure.security import create_access_token
from api.src.use_cases.register_user_use_case import RegisterUserUseCase
from api.src.use_cases.authenticate_user_use_case import AuthenticateUserUseCase
from api.src.use_cases.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_use_case)],
) -> dict:
    try:
        user = await use_case(email=body.email, password=body.password)
        return {"id": user.id.value, "email": user.email}
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/token", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[AuthenticateUserUseCase, Depends(get_authenticate_use_case)],
) -> TokenResponse:
    try:
        user = await use_case(email=form.username, password=form.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail=str(exc), headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(
        data={"sub": user.email, "user_id": user.id.value},
        secret_key=os.environ["SECRET_KEY"],
        expire_minutes=int(os.environ.get("JWT_EXPIRE_MINUTES", "60")),
    )
    return TokenResponse(access_token=token)
