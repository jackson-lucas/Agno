#!/usr/bin/env bash

# This starts the Agno Observability Database
# It is used by the Docker Sandbox to stream telemetry and logs.

docker rm -f agno_observability 2>/dev/null || true
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql \
  -v agno_observability:/var/lib/postgresql \
  -p 5532:5432 \
  --name agno_observability \
  agnohq/pgvector:18
