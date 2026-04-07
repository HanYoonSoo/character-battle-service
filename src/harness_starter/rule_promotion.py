from __future__ import annotations

import json
from pathlib import Path

from harness_starter.ops_models import RuleCandidate
from harness_starter.repo_ops import REPO_ROOT, RULE_CANDIDATES_PATH, load_state


def build_rule_candidates(repo_root: Path = REPO_ROOT, threshold: int = 2) -> list[RuleCandidate]:
    state = load_state(repo_root)
    candidates: list[RuleCandidate] = []

    gate_failures = state.get("gate_failures", {})
    hygiene_findings = state.get("hygiene_findings", {})

    if gate_failures.get("unit_tests", 0) >= threshold:
        candidates.append(
            RuleCandidate(
                code="promote_unit_test_failure",
                title="Promote repeated test failures into a stricter local gate",
                rationale="Unit test failures are recurring often enough to justify a faster pre-merge guard.",
                recommended_action="Add the failing scenario to the deterministic repair gate and tighten local pre-commit execution.",
                evidence=[f"unit_tests failures: {gate_failures['unit_tests']}"],
            )
        )

    if gate_failures.get("hygiene", 0) >= threshold:
        candidates.append(
            RuleCandidate(
                code="promote_hygiene_gate",
                title="Promote hygiene findings into repository policy",
                rationale="Nightly hygiene is finding repeated drift that should fail earlier in the loop.",
                recommended_action="Move the repeated hygiene finding into the always-on repair gate or repository policy checks.",
                evidence=[f"hygiene failures: {gate_failures['hygiene']}"],
            )
        )

    for fingerprint, count in sorted(hygiene_findings.items()):
        if count < threshold:
            continue
        if fingerprint.startswith("unused_harness_module:"):
            candidates.append(
                RuleCandidate(
                    code="promote_dead_code_scan",
                    title="Promote dead-code scan into a required hygiene gate",
                    rationale="Unused harness code keeps reappearing in the repository.",
                    recommended_action="Require the unused harness module scan in repair mode and delete or justify stale modules.",
                    evidence=[f"{fingerprint} repeated {count} times"],
                )
            )
        elif fingerprint.startswith("oversized_harness_file:"):
            candidates.append(
                RuleCandidate(
                    code="promote_file_budget",
                    title="Tighten the harness file-size budget",
                    rationale="Oversized harness modules are drifting past the architecture budget.",
                    recommended_action="Add an explicit max-lines validator and split the flagged module by responsibility.",
                    evidence=[f"{fingerprint} repeated {count} times"],
                )
            )
        elif fingerprint.startswith("documented_test_command_mismatch:"):
            candidates.append(
                RuleCandidate(
                    code="promote_docs_sync_gate",
                    title="Promote docs-command drift into a required check",
                    rationale="The documented test command keeps drifting away from the executable repository gate.",
                    recommended_action="Fail repository policy checks when AGENTS.md or README.md diverge from the canonical test command.",
                    evidence=[f"{fingerprint} repeated {count} times"],
                )
            )

    return _deduplicate_candidates(candidates)


def write_rule_candidate_report(
    candidates: list[RuleCandidate],
    repo_root: Path = REPO_ROOT,
) -> Path:
    report_path = repo_root / ".harness" / "rule_candidates.md"
    report_path.parent.mkdir(exist_ok=True)

    if not candidates:
        content = "# Rule Candidates\n\nNo promotion candidates.\n"
    else:
        lines = ["# Rule Candidates", ""]
        for candidate in candidates:
            lines.append(f"## {candidate.title}")
            lines.append("")
            lines.append(f"- Code: `{candidate.code}`")
            lines.append(f"- Rationale: {candidate.rationale}")
            lines.append(f"- Recommended action: {candidate.recommended_action}")
            if candidate.evidence:
                lines.append(f"- Evidence: {', '.join(candidate.evidence)}")
            lines.append("")
        content = "\n".join(lines)

    report_path.write_text(content, encoding="utf-8")
    return report_path


def render_rule_candidates_json(candidates: list[RuleCandidate]) -> str:
    return json.dumps([candidate.to_dict() for candidate in candidates], indent=2)


def _deduplicate_candidates(candidates: list[RuleCandidate]) -> list[RuleCandidate]:
    seen: set[str] = set()
    unique: list[RuleCandidate] = []
    for candidate in candidates:
        if candidate.code in seen:
            continue
        seen.add(candidate.code)
        unique.append(candidate)
    return unique
