# CI/CD Harness

This document defines how CI/CD must behave so the project stays aligned with harness-engineering principles.

## Core Principle

Jenkins is an executor of deterministic gates. It is not a replacement for the harness.

That means:

- LLM output alone never authorizes deployment
- passing deterministic gates is the only promotion signal
- pipeline logic must live in code

## Routing: Question vs Task

### Question

Examples:

- architecture clarification
- explanation requests
- prompt discussion

Behavior:

- answer only
- no build
- no deploy

### Task

Examples:

- code changes
- Kubernetes manifest changes
- dependency changes
- pipeline changes

Behavior:

- enter CI
- run deterministic gates
- deploy only if gates pass and the branch policy allows it

## Minimum Gate Order

1. repository policy checks
2. sensitive data scan (tokens and private key material)
3. frontend dependency install and production build verification
4. backend `uv.lock` freshness check, locked sync, `pip check`, and runtime import verification
5. lint and formatting checks
6. unit tests
7. API contract checks
8. LLM JSON schema validation checks
9. Kubernetes manifest validation
10. image build
11. image publish to registry reachable by the VM cluster
12. deployment with `kubectl apply -k`
13. smoke test

Current deterministic dependency gates:

- frontend: `npm ci` then `npm run build`
- backend: `uv lock --check`, `uv sync --locked`, `.venv/bin/pip check`, `uv run --locked python -m compileall app`, `uv run --locked python -c "from app.main import app; print(app.title)"`

Local developer counterpart:

- repository-managed `pre-commit` hook runs the bounded `repair` loop before commit creation
- local `pre-commit` must block commits if sensitive tokens or private keys are detected
- deterministic text-lint failures may be auto-fixed and restaged locally
- CI still reruns the gates and remains the only promotion signal

## Promotion Rule

Only deploy artifacts that were built in CI and published to the registry.

Do not deploy:

- images that exist only on a developer laptop
- manual hotfix containers
- unversioned UI changes made directly in Jenkins

## Source Control Trigger Rule

- source control is GitHub
- use SCM polling in the local setup
- do not assume public webhook reachability from GitHub into the local VM cluster

## Repository Harness Jobs

- `repair`: run deterministic gates, allow bounded auto-repair, rerun the gates
- `hygiene`: run scheduled drift and dead-code checks
- `promote`: turn repeated failures into candidate harness rules

For the main deployment pipeline:

- run `gates`, not `repair`, before build and deploy
- do not deploy from a workspace that Jenkins auto-modified during a repair run
- keep `repair`, `hygiene`, and `promote` as separate auxiliary Jenkins jobs when they are needed
- when Jenkins agent Pods run inside Kubernetes, prefer in-cluster ServiceAccount access for `kubectl` instead of a separate kubeconfig credential

Promotion output must not silently rewrite product requirements. Candidate rules should stay outside the approved `docs/` set until reviewed.

## Leaderboard Rule

The Redis leaderboard is derived state.

CI/CD must never assume Redis ranking data is authoritative. If needed, deployment or recovery jobs must be able to rebuild rankings from PostgreSQL battle records.

## Jenkins Configuration Rule

- use `Jenkinsfile`
- keep plugin set minimal and reviewable
- if this repository later owns the Jenkins controller configuration, keep that configuration as code outside UI-only drift
