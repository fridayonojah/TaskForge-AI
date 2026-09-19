#!/bin/bash
set -euo pipefail

export PYTHONPATH=/app/src

echo "Running database migrations..."
cd /app && alembic upgrade head

echo "Starting API server..."
exec uvicorn drivers.rest.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers "${WORKERS:-2}" \
  --log-config /dev/null
