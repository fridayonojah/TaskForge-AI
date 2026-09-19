from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Job:
    id: str
    job_type: str
    status: JobStatus
    payload: dict
    result: dict | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
