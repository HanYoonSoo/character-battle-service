from __future__ import annotations

from pathlib import Path

from harness_starter.ops_models import GateResult, TextLintFinding
from harness_starter.repo_ops import REPO_ROOT


TEXT_FILE_SUFFIXES = {
    ".md",
    ".py",
    ".sh",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_DIRECTORIES = {
    ".cache",
    ".git",
    ".harness",
    ".uv-bootstrap",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def run_text_lint_gate(repo_root: Path = REPO_ROOT) -> GateResult:
    findings = collect_text_lint_findings(repo_root)
    summary = "passed" if not findings else render_text_lint_report(findings)
    return GateResult(
        name="text_lint",
        passed=not findings,
        summary=summary,
        repairable=bool(findings),
        metadata={"findings": [finding.to_dict() for finding in findings]},
    )


def collect_text_lint_findings(repo_root: Path = REPO_ROOT) -> list[TextLintFinding]:
    findings: list[TextLintFinding] = []
    for path in iter_text_files(repo_root):
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                raw_text = handle.read()
        except UnicodeDecodeError:
            continue

        relative_path = path.relative_to(repo_root).as_posix()
        if "\r\n" in raw_text:
            findings.append(
                TextLintFinding(
                    code="crlf_line_endings",
                    message="Text files must use LF line endings.",
                    path=relative_path,
                )
            )
        if raw_text and not raw_text.endswith("\n"):
            findings.append(
                TextLintFinding(
                    code="missing_final_newline",
                    message="Text files must end with a newline.",
                    path=relative_path,
                )
            )
        if any(line.rstrip(" \t") != line for line in raw_text.splitlines()):
            findings.append(
                TextLintFinding(
                    code="trailing_whitespace",
                    message="Text files must not contain trailing whitespace.",
                    path=relative_path,
                )
            )
    return findings


def normalize_text_file(path: Path) -> bool:
    with path.open("r", encoding="utf-8", newline="") as handle:
        raw_text = handle.read()
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")
    normalized = "\n".join(line.rstrip(" \t") for line in lines)
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    if normalized == raw_text:
        return False
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(normalized)
    return True


def render_text_lint_report(findings: list[TextLintFinding]) -> str:
    unique_paths = sorted({finding.path for finding in findings})
    return "Text lint failed for: " + ", ".join(unique_paths)


def iter_text_files(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(repo_root).parts
        if any(part in SKIP_DIRECTORIES or part.endswith(".egg-info") for part in parts):
            continue
        if path.name in {"sitecustomize.py"} or path.suffix in TEXT_FILE_SUFFIXES:
            paths.append(path)
    return paths
