from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from harness_starter.git_hooks import install_git_hooks, run_pre_commit_hook
from harness_starter.hygiene import render_hygiene_report, run_hygiene_checks
from harness_starter.repair import (
    CompositeRepairAgent,
    ExternalCommandRepairAgent,
    SafeFileRepairAgent,
    run_auto_repair,
    run_deterministic_gates,
)
from harness_starter.repo_ops import REPO_ROOT
from harness_starter.rule_promotion import (
    build_rule_candidates,
    render_rule_candidates_json,
    write_rule_candidate_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run repository-level harness operations.")
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root to operate on.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gates_parser = subparsers.add_parser("gates", help="Run deterministic harness gates.")
    gates_parser.add_argument("--json", action="store_true", help="Render gate results as JSON.")

    hygiene_parser = subparsers.add_parser("hygiene", help="Run nightly hygiene checks.")
    hygiene_parser.add_argument("--json", action="store_true", help="Render hygiene findings as JSON.")
    hygiene_parser.add_argument(
        "--fail-on-findings",
        action="store_true",
        help="Return a non-zero exit code when findings are present.",
    )

    repair_parser = subparsers.add_parser("repair", help="Run the automatic repair loop.")
    repair_parser.add_argument("--json", action="store_true", help="Render repair results as JSON.")
    repair_parser.add_argument(
        "--max-attempts",
        type=int,
        default=2,
        help="Maximum repair attempts before escalation.",
    )

    pre_commit_parser = subparsers.add_parser("pre-commit", help="Run the local git pre-commit harness.")
    pre_commit_parser.add_argument("--json", action="store_true", help="Render repair results as JSON.")
    pre_commit_parser.add_argument(
        "--max-attempts",
        type=int,
        default=2,
        help="Maximum repair attempts before escalation.",
    )

    subparsers.add_parser("install-hooks", help="Configure git to use the repository-managed hooks.")

    promote_parser = subparsers.add_parser("promote", help="Build rule promotion candidates.")
    promote_parser.add_argument("--json", action="store_true", help="Render rule candidates as JSON.")
    promote_parser.add_argument(
        "--threshold",
        type=int,
        default=2,
        help="Minimum repetition count before a candidate is emitted.",
    )
    promote_parser.add_argument(
        "--write-report",
        action="store_true",
        help="Write a Markdown report to .harness/rule_candidates.md.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()

    if args.command == "gates":
        results = run_deterministic_gates(repo_root)
        if args.json:
            print(json.dumps([result.to_dict() for result in results], indent=2))
        else:
            for result in results:
                print(f"{result.name}: {'PASS' if result.passed else 'FAIL'}")
                if not result.passed:
                    print(result.summary)
        return 0 if all(result.passed for result in results) else 1

    if args.command == "hygiene":
        findings = run_hygiene_checks(repo_root)
        if args.json:
            print(json.dumps([finding.to_dict() for finding in findings], indent=2))
        else:
            print(render_hygiene_report(findings))
        if args.fail_on_findings and findings:
            return 1
        return 0

    if args.command == "repair":
        agent = CompositeRepairAgent(SafeFileRepairAgent())
        command = os.getenv("HARNESS_REPAIR_COMMAND")
        if command:
            agent = CompositeRepairAgent(SafeFileRepairAgent(), ExternalCommandRepairAgent(command))
        outcome = run_auto_repair(repo_root=repo_root, agent=agent, max_attempts=args.max_attempts)
        if args.json:
            print(json.dumps(outcome.to_dict(), indent=2))
        else:
            print(json.dumps(outcome.to_dict(), indent=2))
        return 0 if outcome.success else 1

    if args.command == "pre-commit":
        outcome = run_pre_commit_hook(repo_root=repo_root, max_attempts=args.max_attempts)
        if args.json:
            print(json.dumps(outcome.to_dict(), indent=2))
        else:
            print(json.dumps(outcome.to_dict(), indent=2))
        return 0 if outcome.success else 1

    if args.command == "install-hooks":
        hooks_path = install_git_hooks(repo_root=repo_root)
        print(hooks_path)
        return 0

    candidates = build_rule_candidates(repo_root=repo_root, threshold=args.threshold)
    if args.write_report:
        report_path = write_rule_candidate_report(candidates, repo_root)
        print(report_path)
    if args.json:
        print(render_rule_candidates_json(candidates))
    else:
        if candidates:
            for candidate in candidates:
                print(f"{candidate.code}: {candidate.title}")
        else:
            print("No promotion candidates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
