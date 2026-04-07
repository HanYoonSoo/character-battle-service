from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from harness_starter.hygiene import DOCUMENTED_TEST_COMMAND, run_hygiene_checks


class HygieneTests(unittest.TestCase):
    def test_reports_missing_jenkins_as_code_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_required_docs(repo_root)
            _write_minimal_kustomize(repo_root)
            (repo_root / ".gitignore").write_text(".harness/\n", encoding="utf-8")
            harness_root = repo_root / "src" / "harness_starter"
            harness_root.mkdir(parents=True)
            (harness_root / "__init__.py").write_text("", encoding="utf-8")
            (harness_root / "ops_cli.py").write_text(
                "from harness_starter import hygiene\n",
                encoding="utf-8",
            )
            (harness_root / "hygiene.py").write_text("", encoding="utf-8")

            findings = run_hygiene_checks(repo_root)
            codes = {finding.code for finding in findings}

            self.assertIn("jenkinsfile_missing", codes)

    def test_passes_when_required_harness_files_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            _write_required_docs(repo_root)
            (repo_root / ".gitignore").write_text(".harness/\n", encoding="utf-8")
            (repo_root / "Jenkinsfile").write_text("pipeline { agent any }\n", encoding="utf-8")
            _write_minimal_kustomize(repo_root)

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

            findings = run_hygiene_checks(repo_root)

            self.assertEqual(findings, [])


def _write_required_docs(repo_root: Path) -> None:
    for filename in ("README.md", "AGENTS.md"):
        (repo_root / filename).write_text(
            f"Run the tests with `{DOCUMENTED_TEST_COMMAND}`.\n",
            encoding="utf-8",
        )


def _write_minimal_kustomize(repo_root: Path) -> None:
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


if __name__ == "__main__":
    unittest.main()
