from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import Protocol

from harness_starter.hygiene import render_hygiene_report, run_hygiene_checks
from harness_starter.ops_models import GateResult, HygieneFinding, RepairOutcome
from harness_starter.repo_ops import (
    COMPILE_COMMAND,
    REPO_ROOT,
    TEST_COMMAND,
    command_to_display,
    record_gate_results,
    record_hygiene_findings,
    record_repair_run,
    run_subprocess_gate,
)
from harness_starter.sensitive_lint import run_sensitive_data_gate
from harness_starter.text_lint import normalize_text_file, run_text_lint_gate


class RepairAgent(Protocol):
    def repair(self, gate: GateResult, repo_root: Path) -> list[str]:
        ...


class SafeFileRepairAgent:
    def repair(self, gate: GateResult, repo_root: Path) -> list[str]:
        applied: list[str] = []
        if gate.name == "text_lint":
            changed_paths = sorted(
                {
                    raw_finding["path"]
                    for raw_finding in gate.metadata.get("findings", [])
                    if raw_finding.get("path")
                }
            )
            for relative_path in changed_paths:
                if normalize_text_file(repo_root / relative_path):
                    applied.append(f"normalize_text_file:{relative_path}")
        findings = _deserialize_findings(gate)
        for finding in findings:
            if finding.code == "harness_state_not_ignored":
                gitignore_path = repo_root / ".gitignore"
                existing = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
                lines = [line for line in existing.splitlines() if line]
                if ".harness/" not in lines:
                    lines.append(".harness/")
                    gitignore_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                    applied.append("ignore_harness_state")
        return applied


class ExternalCommandRepairAgent:
    def __init__(self, command: str) -> None:
        self.command = tuple(shlex.split(command))

    def repair(self, gate: GateResult, repo_root: Path) -> list[str]:
        payload = {
            "gate": gate.to_dict(),
            "repo_root": str(repo_root),
        }
        completed = subprocess.run(
            self.command,
            cwd=repo_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            return []
        return [f"external_agent:{command_to_display(self.command)}"]


class CompositeRepairAgent:
    def __init__(self, *agents: RepairAgent) -> None:
        self.agents = agents

    def repair(self, gate: GateResult, repo_root: Path) -> list[str]:
        applied: list[str] = []
        for agent in self.agents:
            applied.extend(agent.repair(gate, repo_root))
        return applied


def run_deterministic_gates(repo_root: Path = REPO_ROOT) -> list[GateResult]:
    results = [run_sensitive_data_gate(repo_root), run_text_lint_gate(repo_root)]

    if not all(result.passed for result in results):
        record_gate_results(results, repo_root)
        return results

    results.extend(
        [
            run_subprocess_gate(
                name="compile_sources",
                command=COMPILE_COMMAND,
                repairable=False,
                repo_root=repo_root,
            ),
            run_subprocess_gate(
                name="unit_tests",
                command=TEST_COMMAND,
                repairable=True,
                repo_root=repo_root,
            ),
        ]
    )

    if not all(result.passed for result in results):
        record_gate_results(results, repo_root)
        return results

    findings = run_hygiene_checks(repo_root)
    if findings:
        record_hygiene_findings([finding.fingerprint() for finding in findings], repo_root)
    hygiene_result = GateResult(
        name="hygiene",
        passed=not findings,
        summary="passed" if not findings else render_hygiene_report(findings),
        repairable=bool(findings),
        metadata={"findings": [finding.to_dict() for finding in findings]},
    )
    results.append(hygiene_result)
    record_gate_results(results, repo_root)
    return results


def run_auto_repair(
    *,
    repo_root: Path = REPO_ROOT,
    agent: RepairAgent | None = None,
    max_attempts: int = 2,
) -> RepairOutcome:
    repair_agent = agent or CompositeRepairAgent(SafeFileRepairAgent())
    attempts = 0
    applied_repairs: list[str] = []

    while attempts <= max_attempts:
        results = run_deterministic_gates(repo_root)
        failed = next((result for result in results if not result.passed), None)
        if failed is None:
            outcome = RepairOutcome(
                success=True,
                attempts_used=attempts,
                results=results,
                applied_repairs=applied_repairs,
                stopped_reason="all_gates_passed",
            )
            record_repair_run(outcome.to_dict(), repo_root)
            return outcome

        if attempts == max_attempts or not failed.repairable:
            outcome = RepairOutcome(
                success=False,
                attempts_used=attempts,
                results=results,
                applied_repairs=applied_repairs,
                stopped_reason=f"stopped_on_{failed.name}",
            )
            record_repair_run(outcome.to_dict(), repo_root)
            return outcome

        attempts += 1
        applied = repair_agent.repair(failed, repo_root)
        if not applied:
            outcome = RepairOutcome(
                success=False,
                attempts_used=attempts,
                results=results,
                applied_repairs=applied_repairs,
                stopped_reason=f"no_repair_available_for_{failed.name}",
            )
            record_repair_run(outcome.to_dict(), repo_root)
            return outcome
        applied_repairs.extend(applied)

    outcome = RepairOutcome(
        success=False,
        attempts_used=attempts,
        results=results,
        applied_repairs=applied_repairs,
        stopped_reason="max_attempts_exhausted",
    )
    record_repair_run(outcome.to_dict(), repo_root)
    return outcome


def _deserialize_findings(gate: GateResult) -> list[HygieneFinding]:
    raw_findings = gate.metadata.get("findings", [])
    findings: list[HygieneFinding] = []
    for raw in raw_findings:
        findings.append(
            HygieneFinding(
                code=raw["code"],
                message=raw["message"],
                path=raw["path"],
                severity=raw.get("severity", "error"),
                metadata=raw.get("metadata", {}),
            )
        )
    return findings
