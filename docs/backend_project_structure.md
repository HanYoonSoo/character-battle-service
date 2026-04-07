# Backend Project Structure

This project uses a practical layered FastAPI structure intended to stay close to common production patterns.

Reference points:

- FastAPI official docs recommend splitting larger applications into multiple files with `APIRouter` modules instead of one large file.
- FastAPI's official full-stack template uses a dedicated `backend/` folder and a structured backend/frontend split.
- FastAPI official docs recommend `lifespan` for startup and shutdown logic.
- SQLAlchemy official docs document connection-pool settings such as `pool_pre_ping`.

Sources:

- https://fastapi.tiangolo.com/tutorial/bigger-applications/
- https://fastapi.tiangolo.com/advanced/events/
- https://github.com/fastapi/full-stack-fastapi-template
- https://docs.sqlalchemy.org/en/20/core/pooling.html

## Chosen Layout

```text
backend/
  app/
    api/
      deps.py
      router.py
      routes/
    core/
      config.py
    db/
      base.py
      session.py
    models/
    repositories/
    schemas/
    services/
    main.py
  tests/
  pyproject.toml
```

## Why This Structure

### `api/`

- FastAPI routers and request wiring only
- should stay thin
- no business logic here

### `core/`

- application settings
- shared configuration
- cross-cutting utilities

### `db/`

- SQLAlchemy metadata and database session setup

### `models/`

- ORM models mapped to PostgreSQL tables

### `repositories/`

- persistence access layer
- encapsulates query logic so services are not coupled to ORM details

### `schemas/`

- request and response contracts
- Pydantic models for input and output

### `services/`

- business use cases
- anonymous session bootstrap
- character lifecycle rules
- battle orchestration
- leaderboard read model orchestration
- LLM judgment and validation flow

## Practical Rule

If a file starts growing because it handles routing, database access, validation, and domain logic at once, split it by responsibility instead of expanding the file further.

## Suggested First Modules

- `session_service.py`
- `character_service.py`
- `battle_service.py`
- `leaderboard_service.py`
- `llm_judge_service.py`
- `character_repository.py`
- `battle_repository.py`
