from __future__ import annotations
import json
import uuid
from datetime import datetime

import redis.asyncio as aioredis
from domain.entities.job import Job, JobStatus
from ports.queue.job_queue import JobQueue


class ArqJobQueue(JobQueue):
    _KEY_PREFIX = "job:"

    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    async def enqueue(self, job_type: str, payload: dict) -> str:
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "job_type": job_type,
            "status": JobStatus.QUEUED,
            "payload": payload,
            "result": None,
            "error": None,
            "created_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }
        await self._client.set(
            f"{self._KEY_PREFIX}{job_id}",
            json.dumps(job_data),
            ex=3600,
        )
        # Push to ARQ queue (function name matches worker task)
        await self._client.lpush(f"arq:queue:{job_type}", json.dumps({"job_id": job_id, **payload}))
        return job_id

    async def get_job(self, job_id: str) -> Job | None:
        raw = await self._client.get(f"{self._KEY_PREFIX}{job_id}")
        if not raw:
            return None
        data = json.loads(raw)
        return Job(
            id=data["id"],
            job_type=data["job_type"],
            status=JobStatus(data["status"]),
            payload=data["payload"],
            result=data.get("result"),
            error=data.get("error"),
            created_at=datetime.fromisoformat(data["created_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
