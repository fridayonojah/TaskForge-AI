from pydantic import BaseModel


class JobStatusResponse(BaseModel):
    job_id: str
    job_type: str
    status: str
    result: dict | None = None
    error: str | None = None


class JobEnqueuedResponse(BaseModel):
    job_id: str
    status: str
    message: str
