#!/bin/bash
set -euo pipefail

export PYTHONPATH=/app/src

echo "Waiting for migrations to complete..."
sleep 5

echo "Starting ARQ worker..."
exec python -c "
import asyncio, os, sys
sys.path.insert(0, '/app/src')
from arq import run_worker
from infrastructure.worker.settings import WorkerSettings
WorkerSettings.redis_settings = WorkerSettings.get_redis_settings()
asyncio.run(run_worker(WorkerSettings))
"
