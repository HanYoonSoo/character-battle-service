from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from harness_starter.sensitive_lint import run_sensitive_data_gate


class SensitiveLintGateTests(unittest.TestCase):
    def test_passes_for_placeholder_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "README.md").write_text(
                "OPENAI_API_KEY=your_key_here\n",
                encoding="utf-8",
            )

            result = run_sensitive_data_gate(repo_root)

            self.assertTrue(result.passed)
            self.assertEqual(result.summary, "passed")

    def test_detects_private_key_header(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "credentials.pem").write_text(
                "-----BEGIN " + "PRIVATE " + "KEY-----\n",
                encoding="utf-8",
            )

            result = run_sensitive_data_gate(repo_root)

            self.assertFalse(result.passed)
            self.assertEqual(result.name, "sensitive_data")
            self.assertIn("private_key_block", result.summary)

    def test_ignores_harness_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            harness_state = repo_root / ".harness"
            harness_state.mkdir()
            (harness_state / "debug.txt").write_text(
                "token=" + "ghp_" + "1234567890abcdef1234567890abcdef1234\n",
                encoding="utf-8",
            )

            result = run_sensitive_data_gate(repo_root)

            self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
