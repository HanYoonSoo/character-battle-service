from __future__ import annotations

import re
import subprocess
from pathlib import Path

from harness_starter.ops_models import GateResult
from harness_starter.repo_ops import REPO_ROOT


MAX_TEXT_FILE_BYTES = 1_000_000
IGNORED_DIR_NAMES = {
    ".git",
    ".harness",
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
}
SENSITIVE_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (
        "openai_api_key",
        "OpenAI API key pattern was detected.",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "aws_access_key_id",
        "AWS access key ID pattern was detected.",
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    ),
    (
        "github_pat",
        "GitHub personal access token pattern was detected.",
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    ),
    (
        "github_classic_pat",
        "GitHub classic token pattern was detected.",
        re.compile(r"\bghp_[A-Za-z0-9]{36}\b"),
    ),
    (
        "private_key_block",
        "Private key block header was detected.",
        re.compile(r"-----BEGIN (?:RSA|EC|DSA|OPENSSH|PGP|PRIVATE) KEY-----"),
    ),
    (
        "slack_token",
        "Slack token pattern was detected.",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    ),
)


def run_sensitive_data_gate(repo_root: Path = REPO_ROOT) -> GateResult:
    findings = collect_sensitive_data_findings(repo_root)
    return GateResult(
        name="sensitive_data",
        passed=not findings,
        summary="passed" if not findings else render_sensitive_data_report(findings),
        repairable=False,
        metadata={"findings": findings},
    )


def collect_sensitive_data_findings(repo_root: Path = REPO_ROOT) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in _iter_text_files(repo_root):
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for code, message, pattern in SENSITIVE_PATTERNS:
                if not pattern.search(line):
                    continue
                findings.append(
                    {
                        "code": code,
                        "message": message,
                        "path": path.relative_to(repo_root).as_posix(),
                        "line": line_number,
                    }
                )
    return findings


def render_sensitive_data_report(findings: list[dict[str, object]]) -> str:
    lines = ["Sensitive data scan failed."]
    for finding in findings[:20]:
        path = finding["path"]
        line = finding["line"]
        code = finding["code"]
        message = finding["message"]
        lines.append(f"[{code}] {path}:{line} {message}")
    remaining = len(findings) - 20
    if remaining > 0:
        lines.append(f"... and {remaining} more finding(s).")
    return "\n".join(lines)


def _iter_text_files(repo_root: Path) -> list[Path]:
    indexed_paths = _list_git_index_paths(repo_root)
    if indexed_paths is not None:
        candidates: list[Path] = []
        for relative_path in indexed_paths:
            path = repo_root / relative_path
            if not path.exists() or not path.is_file():
                continue
            if set(relative_path.parts) & IGNORED_DIR_NAMES:
                continue
            if path.stat().st_size > MAX_TEXT_FILE_BYTES:
                continue
            try:
                path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            candidates.append(path)
        return sorted(candidates)

    candidates: list[Path] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = set(path.relative_to(repo_root).parts)
        if relative_parts & IGNORED_DIR_NAMES:
            continue
        if path.stat().st_size > MAX_TEXT_FILE_BYTES:
            continue
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        candidates.append(path)
    return candidates


def _list_git_index_paths(repo_root: Path) -> list[Path] | None:
    completed = subprocess.run(
        ("git", "ls-files", "--cached", "-z"),
        cwd=repo_root,
        capture_output=True,
        text=False,
        check=False,
    )
    if completed.returncode != 0:
        return None
    if not completed.stdout:
        return []
    return [Path(raw.decode("utf-8")) for raw in completed.stdout.split(b"\x00") if raw]
