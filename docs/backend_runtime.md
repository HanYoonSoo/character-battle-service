# Backend Runtime

This document fixes the practical backend runtime shape so implementation decisions stay aligned with harness-engineering rules.

## FastAPI Runtime Pattern

Use FastAPI `lifespan` to initialize and close shared resources:

- SQLAlchemy async engine
- Redis client
- OpenAI client

Why:

- resource ownership is explicit
- startup and shutdown are deterministic
- routes do not create heavyweight clients ad hoc

## Local Python Environment

Use Python 3.11 with `uv` and a committed `uv.lock`.

Current rule:

- backend commands should run from the `backend/.venv` created by `uv sync`
- backend dependency changes must update `backend/uv.lock`
- CI, Docker, and Jenkins should install from the lock file, not from floating resolution

Why:

- the backend package declares `requires-python >= 3.11`
- the system `python3` may point to an older interpreter
- a committed lock file keeps FastAPI, SQLAlchemy, Redis, and OpenAI dependencies reproducible

Minimal local verification commands:

- `UV_CACHE_DIR=/tmp/uv-cache uv lock --check`
- `UV_CACHE_DIR=/tmp/uv-cache uv sync --locked`
- `.venv/bin/pip check`
- `uv run --locked python -m compileall app`
- `uv run --locked python -c "from app.main import app; print(app.title)"`

## Database Pooling

Use SQLAlchemy async engine pooling with explicit settings.

Current defaults:

- `pool_pre_ping = true`
- `pool_size = 5`
- `max_overflow = 10`
- `pool_timeout = 30`
- `pool_recycle = 1800`

Why this shape:

- `pool_pre_ping` helps avoid stale connections
- a bounded pool is predictable in local and small-cluster environments
- these values are small enough for local development and easy to tune later

## Session Pattern

- use request-scoped `AsyncSession`
- keep commit boundaries in services
- keep repositories focused on query logic
- set `expire_on_commit = false` for practical FastAPI service-layer usage

## Local Schema Bootstrap

For local development, the backend currently supports startup-time schema creation.

Rule:

- acceptable for local bootstrap
- production CI/CD should move to explicit migrations instead of relying on startup schema creation

## Battle Persistence Rule

Battle history must be renderable even after character soft deletion.

Implementation consequence:

- persist character snapshots inside battle records
- do not depend on live character rows for public history rendering

## Async Battle Job Rule

Battle judgment now runs asynchronously after the initial HTTP request.

Implementation consequence:

- create the battle row first with a `pending` status
- run the LLM judgment in a background job that opens its own database session
- never reuse the request-scoped session inside a background task
- update the battle row to `*_completed` or `*_failed` in the background job

## Leaderboard Runtime Rule

Redis leaderboard data is a derived read model.

Implementation consequence:

- write battle truth to PostgreSQL first
- update Redis leaderboard after verified battle persistence
- tolerate Redis leaderboard rebuilds from PostgreSQL if needed
