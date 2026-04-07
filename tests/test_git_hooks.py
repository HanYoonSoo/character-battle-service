from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from harness_starter.git_hooks import install_git_hooks, run_pre_commit_hook
from harness_starter.hygiene import DOCUMENTED_TEST_COMMAND


@unittest.skipIf(shutil.which("git") is None, "git is required for hook tests")
class GitHookTests(unittest.TestCase):
    def test_install_hooks_sets_core_hooks_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _init_git_repo(repo_root)
            hooks_dir = repo_root / ".githooks"
            hooks_dir.mkdir()
            (hooks_dir / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

            hooks_path = install_git_hooks(repo_root)

            self.assertEqual(hooks_path, ".githooks")
            current = subprocess.run(
                ("git", "config", "--local", "--get", "core.hooksPath"),
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(current.stdout.strip(), ".githooks")

    def test_pre_commit_restages_repaired_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _init_git_repo(repo_root)
            _write_minimal_repo(repo_root)
            readme_path = repo_root / "README.md"
            readme_path.write_text(
                f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.  ",
                encoding="utf-8",
            )
            _git(repo_root, "add", "README.md", "AGENTS.md", ".gitignore", "Jenkinsfile")
            _git(repo_root, "add", "infra/k8s/base/kustomization.yaml", "infra/k8s/base/app-configmap.yaml")
            _git(repo_root, "add", "src/harness_starter/__init__.py", "src/harness_starter/ops_cli.py", "src/harness_starter/hygiene.py")

            outcome = run_pre_commit_hook(repo_root=repo_root, max_attempts=1)

            self.assertTrue(outcome.success)
            self.assertIn("normalize_text_file:README.md", outcome.applied_repairs)
            working_tree = readme_path.read_text(encoding="utf-8")
            index_copy = _git(repo_root, "show", ":README.md")
            self.assertEqual(working_tree, index_copy)
            self.assertEqual(working_tree, f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n")

    def test_pre_commit_ignores_unresolvable_external_repair_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _init_git_repo(repo_root)
            _write_minimal_repo(repo_root)
            readme_path = repo_root / "README.md"
            readme_path.write_text(
                f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.  ",
                encoding="utf-8",
            )
            _git(repo_root, "add", "README.md", "AGENTS.md", ".gitignore", "Jenkinsfile")
            _git(repo_root, "add", "infra/k8s/base/kustomization.yaml", "infra/k8s/base/app-configmap.yaml")
            _git(repo_root, "add", "src/harness_starter/__init__.py", "src/harness_starter/ops_cli.py", "src/harness_starter/hygiene.py")

            with patch.dict(os.environ, {"HARNESS_REPAIR_COMMAND": "__not_a_real_command__"}, clear=False):
                outcome = run_pre_commit_hook(repo_root=repo_root, max_attempts=1)

            self.assertTrue(outcome.success)
            self.assertIn("normalize_text_file:README.md", outcome.applied_repairs)


def _init_git_repo(repo_root: Path) -> None:
    _git(repo_root, "init")
    _git(repo_root, "config", "user.name", "Codex Test")
    _git(repo_root, "config", "user.email", "codex@example.com")


def _write_minimal_repo(repo_root: Path) -> None:
    (repo_root / "README.md").write_text(
        f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n",
        encoding="utf-8",
    )
    (repo_root / "AGENTS.md").write_text(
        f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n",
        encoding="utf-8",
    )
    (repo_root / ".gitignore").write_text(".harness/\n", encoding="utf-8")
    (repo_root / "Jenkinsfile").write_text("pipeline { agent any }\n", encoding="utf-8")

    base_path = repo_root / "infra" / "k8s" / "base"
    base_path.mkdir(parents=True)
    (base_path / "kustomization.yaml").write_text(
        "resources:\n  - app-configmap.yaml\n",
        encoding="utf-8",
    )
    (base_path / "app-configmap.yaml").write_text(
        "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: app-config\n",
        encoding="utf-8",
    )

    harness_root = repo_root / "src" / "harness_starter"
    harness_root.mkdir(parents=True)
    (harness_root / "__init__.py").write_text("", encoding="utf-8")
    (harness_root / "ops_cli.py").write_text(
        "from harness_starter import hygiene\n",
        encoding="utf-8",
    )
    (harness_root / "hygiene.py").write_text(
        "def sentinel() -> str:\n    return 'ok'\n",
        encoding="utf-8",
    )

    (repo_root / "tests").mkdir()


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", *args),
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout
