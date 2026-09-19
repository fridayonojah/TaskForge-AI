import os
from infrastructure.worker.tasks import plan_trip_task, research_industry_task


class WorkerSettings:
    functions = [plan_trip_task, research_industry_task]
    redis_settings = None  # set from env at startup

    @classmethod
    def get_redis_settings(cls):
        from arq.connections import RedisSettings
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        # arq RedisSettings parses host/port
        if redis_url.startswith("redis://"):
            parts = redis_url.replace("redis://", "").split(":")
            host = parts[0]
            port = int(parts[1].split("/")[0]) if len(parts) > 1 else 6379
            return RedisSettings(host=host, port=port)
        return RedisSettings()
