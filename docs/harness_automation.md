# Harness Automation

This document defines the repository-level harness loops that run around code changes.

## Repair Loop

Purpose:

- run deterministic gates
- stop on the first failing gate
- allow safe auto-fixes
- allow an optional external coding agent command for harder deterministic failures

Rules:

- only deterministic failures may enter the auto-repair loop
- every repair attempt must rerun the gates
- attempts are capped
- unresolved failures must escalate instead of looping forever

Current gate set:

- sensitive data scan
- text lint normalization
- source compilation
- root unit tests
- repository hygiene checks

## Local Pre-Commit Hook

Purpose:

- run the repair loop before a commit is created
- block commits that include sensitive tokens or private key material
- auto-fix deterministic text-lint failures
- restage repaired files so the commit contains the fixed content

Rules:

- the hook must stay bounded and deterministic
- sensitive data findings are blocking and must not be auto-committed
- unresolved failures must block the commit instead of silently bypassing the harness
- optional external repair commands may participate through `HARNESS_REPAIR_COMMAND`

## Hygiene Loop

Purpose:

- detect document drift
- detect repository-policy drift
- detect harness dead code

Current checks:

- documented test command drift in `README.md` and `AGENTS.md`
- `Jenkinsfile` exists for the external Jenkins controller
- `.harness/` runtime state stays ignored
- Kustomize base does not reference missing manifests
- harness Python files stay under the line budget
- unused harness modules are reported

## Rule Promotion Loop

Purpose:

- convert repeated failures into stronger harness rules

Rules:

- promotion reads the stored failure history under `.harness/`
- candidate rules are written outside `docs/` so they do not become approved product knowledge automatically
- promotion may suggest new tests, validators, or CI gates
- promotion does not silently change product requirements
