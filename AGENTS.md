# AGENTS.md

## Purpose
- This repository is a starter project for learning harness engineering by building a character battle website.
- Prefer small, verifiable changes over broad autonomous behavior.
- Treat the project as practice for production-minded software structure, not as a throwaway demo.

## Runtime Rules
- Treat the contents of `docs/` as the only approved knowledge source for answers.
- Do not add external network calls unless the user explicitly asks for them.
- Do not bypass validators to make a run "look successful".
- If a response cannot be grounded in `docs/`, return a follow-up question instead of guessing.
- If website requirements are underspecified, ask for clarification before generating large code changes.
- Route simple questions and executable tasks differently.
- Simple questions must not trigger CI/CD or deployment side effects.
- Executable tasks may trigger CI/CD only after deterministic harness gates pass.
- Deterministic gate failures may enter a bounded auto-repair loop before human escalation.
- Battle outcomes must always produce exactly one winner. Draws are not allowed.
- The backend must not be publicly exposed. Only the frontend may publish a host port by default.
- Authentication is intentionally omitted for v1, but anonymous users still need stable identification.
- Follow the backend package layout documented in `docs/backend_project_structure.md` unless there is a strong reason to revise it.
- Jenkins configuration must live as code, not as UI-only drift.

## Code Rules
- Keep the harness loop deterministic where possible.
- Add or update tests for behavior changes in `src/`.
- Keep new dependencies optional unless they are required for the core loop.
- Avoid duplicated logic when a shared abstraction or helper would make the code clearer.
- Do not collapse the project into a single large file.
- Prefer production-oriented structure over tutorial-style shortcuts.
- Favor object-oriented design when it improves separation of responsibility and maintainability.
- Model domain concepts explicitly: anonymous user, character, battle, judgment.
- Keep LLM prompt construction and output validation isolated from controllers.
- Use the React + Vite frontend structure and the FastAPI backend structure documented in `docs/`.
- Enforce structured LLM outputs with JSON schema validation before persistence.
- Treat Redis leaderboard data as a derived read model, not the source of truth.
- Use GitHub polling for Jenkins triggers in the local environment unless a deliberate webhook exposure strategy is added later.
- Run periodic hygiene scans to detect repository drift and dead code.
- Promote repeated failures into stronger tests, validators, or CI gates instead of re-fixing them forever.

## Done Criteria
- `python3 -m unittest discover -s tests -p "test_*.py"` passes.
- Documentation reflects any workflow or constraint changes.
