from __future__ import annotations

import re
from pathlib import Path

from harness_starter.ops_models import HygieneFinding
from harness_starter.repo_ops import (
    REPO_ROOT,
)


DOCUMENTED_TEST_COMMAND = 'python3 -m unittest discover -s tests -p "test_*.py"'
MAX_HARNESS_FILE_LINES = 300


def run_hygiene_checks(repo_root: Path = REPO_ROOT) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    findings.extend(check_documented_test_command(repo_root))
    findings.extend(check_harness_state_ignored(repo_root))
    findings.extend(check_jenkins_as_code(repo_root))
    findings.extend(check_kustomize_resource_paths(repo_root))
    findings.extend(check_harness_file_sizes(repo_root))
    findings.extend(check_unused_harness_modules(repo_root))
    return findings


def check_documented_test_command(repo_root: Path) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    for path in (repo_root / "README.md", repo_root / "AGENTS.md"):
        if not path.exists():
            findings.append(
                HygieneFinding(
                    code="documented_test_command_missing_file",
                    message="Expected documentation file is missing.",
                    path=path.relative_to(repo_root).as_posix(),
                )
            )
            continue
        text = path.read_text(encoding="utf-8")
        if DOCUMENTED_TEST_COMMAND not in text:
            findings.append(
                HygieneFinding(
                    code="documented_test_command_mismatch",
                    message="Documented test command drifted from the repository gate.",
                    path=path.relative_to(repo_root).as_posix(),
                    metadata={"expected_command": DOCUMENTED_TEST_COMMAND},
                )
            )
    return findings


def check_harness_state_ignored(repo_root: Path) -> list[HygieneFinding]:
    path = repo_root / ".gitignore"
    if not path.exists():
        return [
            HygieneFinding(
                code="gitignore_missing",
                message="Repository is missing .gitignore for harness state files.",
                path=".gitignore",
            )
        ]

    text = path.read_text(encoding="utf-8")
    if ".harness/" in text.splitlines():
        return []
    return [
        HygieneFinding(
            code="harness_state_not_ignored",
            message="Harness runtime state should not be committed.",
            path=".gitignore",
        )
    ]


def check_jenkins_as_code(repo_root: Path) -> list[HygieneFinding]:
    path = repo_root / "Jenkinsfile"
    if path.exists():
        return []
    return [
        HygieneFinding(
            code="jenkinsfile_missing",
            message="Jenkinsfile is required for harness CI.",
            path=path.relative_to(repo_root).as_posix(),
        )
    ]


def check_kustomize_resource_paths(repo_root: Path) -> list[HygieneFinding]:
    path = repo_root / "infra" / "k8s" / "base" / "kustomization.yaml"
    if not path.exists():
        return [
            HygieneFinding(
                code="kustomization_missing",
                message="Kustomize base manifest is missing.",
                path=path.relative_to(repo_root).as_posix(),
            )
        ]

    findings: list[HygieneFinding] = []
    text = path.read_text(encoding="utf-8")
    resource_paths = _extract_kustomize_resources(text)
    for resource in resource_paths:
        if not (path.parent / resource).exists():
            findings.append(
                HygieneFinding(
                    code="kustomize_resource_missing",
                    message="Kustomization references a missing manifest.",
                    path=(path.parent / resource).relative_to(repo_root).as_posix(),
                    metadata={"kustomization": path.relative_to(repo_root).as_posix()},
                )
            )
    return findings


def check_harness_file_sizes(repo_root: Path, max_lines: int = MAX_HARNESS_FILE_LINES) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []
    harness_root = repo_root / "src" / "harness_starter"
    if not harness_root.exists():
        return findings

    for path in sorted(harness_root.rglob("*.py")):
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count <= max_lines:
            continue
        findings.append(
            HygieneFinding(
                code="oversized_harness_file",
                message="Harness file exceeded the repository line budget.",
                path=path.relative_to(repo_root).as_posix(),
                severity="warning",
                metadata={"line_count": line_count, "max_lines": max_lines},
            )
        )
    return findings


def check_unused_harness_modules(repo_root: Path) -> list[HygieneFinding]:
    harness_root = repo_root / "src" / "harness_starter"
    if not harness_root.exists():
        return []

    entrypoint_allowlist = {"__init__", "cli", "ops_cli"}
    searchable_text = _collect_repo_text(repo_root)
    findings: list[HygieneFinding] = []

    for path in sorted(harness_root.glob("*.py")):
        module_name = path.stem
        if module_name in entrypoint_allowlist:
            continue
        dotted_name = f"harness_starter.{module_name}"
        module_hits = len(re.findall(rf"\b{re.escape(dotted_name)}\b", searchable_text))
        module_hits += len(re.findall(rf"\b{re.escape(module_name)}\b", searchable_text))
        if module_hits == 0:
            findings.append(
                HygieneFinding(
                    code="unused_harness_module",
                    message="Harness module is not referenced by the repository.",
                    path=path.relative_to(repo_root).as_posix(),
                    severity="warning",
                )
            )
    return findings


def render_hygiene_report(findings: list[HygieneFinding]) -> str:
    if not findings:
        return "No hygiene findings."
    lines = []
    for finding in findings:
        lines.append(f"[{finding.severity}] {finding.code} {finding.path}: {finding.message}")
    return "\n".join(lines)


def _collect_repo_text(repo_root: Path) -> str:
    chunks: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".md", ".yml", ".yaml", ""}:
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    return "\n".join(chunks)


def _extract_kustomize_resources(text: str) -> list[str]:
    resources: list[str] = []
    in_resources = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "resources:":
            in_resources = True
            continue
        if in_resources and not raw_line.startswith(" "):
            in_resources = False
        if in_resources and stripped.startswith("- "):
            resources.append(stripped[2:].strip())
    return resources
