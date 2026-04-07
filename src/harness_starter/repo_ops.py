from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from harness_starter.ops_models import GateResult


REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS_STATE_DIR = REPO_ROOT / ".harness"
STATE_PATH = HARNESS_STATE_DIR / "state.json"
RULE_CANDIDATES_PATH = HARNESS_STATE_DIR / "rule_candidates.md"
README_PATH = REPO_ROOT / "README.md"
AGENTS_PATH = REPO_ROOT / "AGENTS.md"
GITHUB_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
JENKINSFILE_PATH = REPO_ROOT / "Jenkinsfile"
KUSTOMIZATION_PATH = REPO_ROOT / "infra" / "k8s" / "base" / "kustomization.yaml"
TEST_COMMAND = (
    sys.executable,
    "-m",
    "unittest",
    "discover",
    "-s",
    "tests",
    "-p",
    "test_*.py",
)
COMPILE_COMMAND = (
    sys.executable,
    "-m",
    "compileall",
    "src",
    "tests",
)


def command_to_display(command: tuple[str, ...]) -> str:
    return shlex.join(command)


def ensure_harness_state_dir(repo_root: Path = REPO_ROOT) -> Path:
    path = repo_root / ".harness"
    path.mkdir(exist_ok=True)
    return path


def load_state(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    state_path = repo_root / ".harness" / "state.json"
    if not state_path.exists():
        return {
            "gate_failures": {},
            "hygiene_findings": {},
            "repair_runs": [],
        }
    return json.loads(state_path.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any], repo_root: Path = REPO_ROOT) -> None:
    ensure_harness_state_dir(repo_root)
    state_path = repo_root / ".harness" / "state.json"
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def record_gate_results(results: list[GateResult], repo_root: Path = REPO_ROOT) -> None:
    state = load_state(repo_root)
    gate_failures = state.setdefault("gate_failures", {})
    for result in results:
        if result.passed:
            continue
        key = result.name
        gate_failures[key] = gate_failures.get(key, 0) + 1
    save_state(state, repo_root)


def record_hygiene_findings(fingerprints: list[str], repo_root: Path = REPO_ROOT) -> None:
    state = load_state(repo_root)
    finding_counts = state.setdefault("hygiene_findings", {})
    for fingerprint in fingerprints:
        finding_counts[fingerprint] = finding_counts.get(fingerprint, 0) + 1
    save_state(state, repo_root)


def record_repair_run(payload: dict[str, Any], repo_root: Path = REPO_ROOT) -> None:
    state = load_state(repo_root)
    repair_runs = state.setdefault("repair_runs", [])
    repair_runs.append(payload)
    state["repair_runs"] = repair_runs[-20:]
    save_state(state, repo_root)


def run_subprocess_gate(
    *,
    name: str,
    command: tuple[str, ...],
    repairable: bool,
    repo_root: Path = REPO_ROOT,
) -> GateResult:
    pycache_root = ensure_harness_state_dir(repo_root) / "pycache"
    pycache_root.mkdir(exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONPYCACHEPREFIX", str(pycache_root))
    completed = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    passed = completed.returncode == 0
    return GateResult(
        name=name,
        passed=passed,
        summary="passed" if passed else "command failed",
        repairable=repairable,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )
