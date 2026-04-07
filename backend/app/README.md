# Backend App Layout

Suggested internal modules:

- `api/`: routers and dependency wiring
- `core/`: configuration and shared application concerns
- `db/`: SQLAlchemy base and database session setup
- `models/`: ORM tables
- `repositories/`: persistence access layer
- `schemas/`: request and response contracts
- `services/`: session, character, battle, and LLM orchestration logic
