# Harness Starter

Minimal harness-engineering starter project built from an empty repository.

Current learning goal: build a character battle website while enforcing harness constraints that keep the codebase maintainable and close to real production structure.

This repository demonstrates the four practical pillars from the harness-engineering workflow:

1. Machine-readable agent rules in `AGENTS.md`
2. Deterministic validation gates in `tests/` and CI
3. Explicit tool and data boundaries in the code structure
4. A feedback loop in the harness execution retry logic

## Project Layout

```text
.
├── AGENTS.md
├── README.md
├── backend/
├── frontend/
├── infra/
├── docs/
│   ├── api_contract.md
│   ├── architecture.md
│   ├── battle_rules.md
│   ├── harness_automation.md
│   ├── engineering_rules.md
│   ├── product_brief.md
│   └── site_scope.md
├── evals/
│   └── sample_eval.jsonl
├── src/
│   └── harness_starter/
│       ├── cli.py
│       ├── context_manager.py
│       ├── harness_loop.py
│       ├── models.py
│       ├── router.py
│       ├── validators.py
│       └── workers.py
└── tests/
    ├── test_context_manager.py
    ├── test_harness_loop.py
    └── test_validators.py
```

## What The Starter Does

- Reads only the local `docs/` directory as context
- Routes unclear requests to a clarification path
- Runs a bounded plan -> answer -> validate -> retry loop
- Rejects answers that are missing citations or cite text outside the approved context
- Provides repository-level repair, hygiene, and rule-promotion loops for deterministic CI work
- Captures code-quality constraints such as avoiding duplication and oversized single-file implementations
- Documents a concrete target service: anonymous character creation and LLM-judged 1:1 battles
- Pins the implementation stack to React + Vite, FastAPI, Redis, PostgreSQL, and pgvector

## Quick Start

Create a virtual environment if you want one:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Run the tests:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Run the local rules-based worker:

```bash
PYTHONPATH=src python3 -m harness_starter.cli "Build a docs-grounded assistant"
```

Run the repository repair loop:

```bash
python3 -m harness_starter.ops_cli repair --max-attempts 2
```

Install the repository-managed pre-commit hook:

```bash
python3 -m harness_starter.ops_cli install-hooks
```

The pre-commit hook runs the repair loop locally, auto-fixes deterministic text-lint failures, restages repaired files, and blocks the commit only when the bounded repair loop cannot recover.

Run the nightly hygiene scan:

```bash
python3 -m harness_starter.ops_cli hygiene --fail-on-findings
```

Generate rule-promotion candidates:

```bash
python3 -m harness_starter.ops_cli promote --threshold 2 --write-report
```

If you want to wire in a live OpenAI worker later, install the optional package and set `OPENAI_API_KEY`:

```bash
pip install -e ".[openai]"
PYTHONPATH=src python3 -m harness_starter.cli --worker openai "Summarize the project rules"
```

## Suggested Next Steps

1. Add migrations and move local schema bootstrap behind migration-driven flow.
2. Connect the React pages to the implemented backend APIs.
3. Configure a reachable local registry for VM-cluster image pulls.
4. Add backend integration tests once Python dependencies are installed locally.
5. Extend the existing Jenkins `Jenkinsfile` with image build, push, and deploy stages after the application flow is stable.

## Current Local Verification

Frontend:

```bash
cd frontend
npm install
npm run build
```

Frontend dev server:

```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

Backend:

```bash
cd backend
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked
.venv/bin/pip check
uv run --locked python -m compileall app
uv run --locked python -c "from app.main import app; print(app.title)"
```

These backend commands assume `uv` is already installed on the machine.

Backend dev server:

```bash
cd backend
DATABASE_URL=postgresql+psycopg://app:app@localhost:15432/character_battle \
REDIS_URL=redis://localhost:16379/0 \
OPENAI_API_KEY=your_key_here \
uv run --locked uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Compose infrastructure only:

```bash
docker compose -f infra/docker-compose.infra.yml up -d
```

Published host ports:

- PostgreSQL: `15432`
- Redis: `16379`

Full local stack with frontend container:

```bash
cp .env.example .env
OPENAI_API_KEY=your_key_here \
docker compose up --build -d
```

Published host ports:

- frontend: `13000`
- PostgreSQL: `15432`
- Redis: `16379`

The backend is intentionally kept on the internal Compose network to match the harness rule that only the frontend is externally reachable by default.

Default Compose entrypoint:

- [`docker-compose.yml`](/Users/hanyoonsoo/harness-engineering-playground/docker-compose.yml)
- run from the repository root so `.env` is loaded automatically
# character-battle-service
