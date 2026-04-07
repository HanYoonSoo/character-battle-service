from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from harness_starter.hygiene import DOCUMENTED_TEST_COMMAND
from harness_starter.repair import run_auto_repair


class RepairLoopTests(unittest.TestCase):
    def test_safe_repair_adds_harness_state_ignore_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_minimal_repo(repo_root, include_harness_ignore=False)

            outcome = run_auto_repair(repo_root=repo_root, max_attempts=1)

            self.assertTrue(outcome.success)
            self.assertIn("ignore_harness_state", outcome.applied_repairs)
            gitignore_text = (repo_root / ".gitignore").read_text(encoding="utf-8")
            self.assertIn(".harness/", gitignore_text)

    def test_safe_repair_normalizes_text_lint_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_minimal_repo(repo_root, include_harness_ignore=True)
            (repo_root / "README.md").write_text(
                f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.  ",
                encoding="utf-8",
            )

            outcome = run_auto_repair(repo_root=repo_root, max_attempts=1)

            self.assertTrue(outcome.success)
            self.assertIn("normalize_text_file:README.md", outcome.applied_repairs)
            repaired_text = (repo_root / "README.md").read_text(encoding="utf-8")
            self.assertEqual(repaired_text, f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n")

    def test_sensitive_data_gate_blocks_repair_loop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_minimal_repo(repo_root, include_harness_ignore=True)
            (repo_root / "leak.txt").write_text(
                "token=" + "ghp_" + "1234567890abcdef1234567890abcdef1234\n",
                encoding="utf-8",
            )

            outcome = run_auto_repair(repo_root=repo_root, max_attempts=2)

            self.assertFalse(outcome.success)
            self.assertEqual(outcome.attempts_used, 0)
            self.assertEqual(outcome.stopped_reason, "stopped_on_sensitive_data")


def _write_minimal_repo(repo_root: Path, *, include_harness_ignore: bool) -> None:
    for filename in ("README.md", "AGENTS.md"):
        (repo_root / filename).write_text(
            f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n",
            encoding="utf-8",
        )

    gitignore_lines = [".venv/"]
    if include_harness_ignore:
        gitignore_lines.append(".harness/")
    (repo_root / ".gitignore").write_text("\n".join(gitignore_lines) + "\n", encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
