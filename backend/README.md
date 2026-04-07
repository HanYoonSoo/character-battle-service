# Backend Structure

Recommended backend responsibilities:

- expose internal-only HTTP APIs
- manage anonymous sessions
- persist characters and battle results
- assemble LLM judge prompts
- validate and retry battle judgments before returning them

Suggested package layout:

```text
app/
  api/
    routes/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
  main.py
tests/
```

Current implementation notes:

- `api/` only wires requests to services
- `services/` owns validation and orchestration logic
- `repositories/` contain PostgreSQL query code
- `main.py` is the FastAPI entrypoint
- FastAPI `lifespan` initializes the async database engine, Redis client, and OpenAI client
- request-scoped async DB sessions are used through dependency injection
- `session_service.py` now wires Redis-backed anonymous sessions to PostgreSQL anonymous users
- character deletion is implemented as soft delete and battle history uses stored snapshots

## Local Setup

Use Python 3.11 and `uv` for backend work.

If `uv` is not installed yet, install it first with your preferred method, then continue with the commands below.

```bash
cd backend
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked
```

Minimal local verification:

```bash
.venv/bin/pip check
uv run --locked python -m compileall app
uv run --locked python -c "from app.main import app; print(app.title)"
```

Run the backend locally:

```bash
cd backend
DATABASE_URL=postgresql+psycopg://app:app@localhost:15432/character_battle \
REDIS_URL=redis://localhost:16379/0 \
OPENAI_API_KEY=your_key_here \
uv run --locked uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Note:

- backend dependency changes should update `uv.lock`
- when running the backend on the host machine, `DATABASE_URL` and `REDIS_URL` must point to host-reachable services
- the local Compose infrastructure publishes PostgreSQL on `15432` and Redis on `16379`
- the default in-code values (`postgres`, `redis`) are for container or cluster networking, not direct host execution

The target is the structure documented in [docs/backend_project_structure.md](/Users/hanyoonsoo/harness-engineering-playground/docs/backend_project_structure.md).

Suggested next implementation order:

- add migrations and disable startup auto-create outside local bootstrap
- add runtime dependency installation and backend test execution
- connect frontend screens to the backend routes
- add Jenkins pipeline and Kubernetes delivery automation
- add observability and smoke checks

Suggested package layout reference:

```text
app/
  api/
  core/
  db/
  models/
  repositories/
  schemas/
  services/
tests/
```
