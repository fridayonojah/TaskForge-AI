from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from use_cases.exceptions import (
    EmptyQueryError,
    PlanningFailedError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    JobNotFoundError,
    ServiceUnavailableError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmptyQueryError)
    async def empty_query_handler(request: Request, exc: EmptyQueryError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"message": str(exc)})

    @app.exception_handler(PlanningFailedError)
    async def planning_failed_handler(request: Request, exc: PlanningFailedError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"message": str(exc)})

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"message": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_creds_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"message": str(exc)})

    @app.exception_handler(JobNotFoundError)
    async def job_not_found_handler(request: Request, exc: JobNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"message": str(exc)})

    @app.exception_handler(ServiceUnavailableError)
    async def service_unavailable_handler(request: Request, exc: ServiceUnavailableError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"message": str(exc)})
