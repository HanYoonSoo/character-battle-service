from __future__ import annotations

import os
import subprocess
from pathlib import Path

from harness_starter.ops_models import RepairOutcome
from harness_starter.repair import (
    CompositeRepairAgent,
    ExternalCommandRepairAgent,
    SafeFileRepairAgent,
    run_auto_repair,
)
from harness_starter.repo_ops import REPO_ROOT


HOOKS_DIR = ".githooks"
PRE_COMMIT_HOOK = Path(HOOKS_DIR) / "pre-commit"


def install_git_hooks(repo_root: Path = REPO_ROOT) -> str:
    hook_path = repo_root / PRE_COMMIT_HOOK
    if not hook_path.exists():
        raise FileNotFoundError(f"Missing git hook script: {hook_path}")

    hook_path.chmod(hook_path.stat().st_mode | 0o111)
    completed = subprocess.run(
        ("git", "config", "--local", "core.hooksPath", HOOKS_DIR),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Failed to configure core.hooksPath.")
    return HOOKS_DIR


def run_pre_commit_hook(repo_root: Path = REPO_ROOT, max_attempts: int = 2) -> RepairOutcome:
    staged_paths = _list_staged_paths(repo_root)
    if not staged_paths:
        return RepairOutcome(
            success=True,
            attempts_used=0,
            results=[],
            stopped_reason="no_staged_paths",
        )

    agent = CompositeRepairAgent(SafeFileRepairAgent())
    command = os.getenv("HARNESS_REPAIR_COMMAND")
    if command:
        agent = CompositeRepairAgent(SafeFileRepairAgent(), ExternalCommandRepairAgent(command))

    outcome = run_auto_repair(repo_root=repo_root, agent=agent, max_attempts=max_attempts)
    if outcome.success:
        _restage_paths(repo_root, staged_paths)
    return outcome


def _list_staged_paths(repo_root: Path) -> list[str]:
    completed = subprocess.run(
        ("git", "diff", "--cached", "--name-only", "--diff-filter=ACMRD"),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "Failed to inspect staged paths.")
    return [line for line in completed.stdout.splitlines() if line]


def _restage_paths(repo_root: Path, staged_paths: list[str]) -> None:
    refresh = subprocess.run(
        ("git", "add", "--update"),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if refresh.returncode != 0:
        raise RuntimeError(refresh.stderr.strip() or "Failed to refresh staged tracked files.")

    existing_paths = [path for path in staged_paths if (repo_root / path).exists()]
    if not existing_paths:
        return

    restage = subprocess.run(
        ("git", "add", "--", *existing_paths),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if restage.returncode != 0:
        raise RuntimeError(restage.stderr.strip() or "Failed to restage repaired files.")
