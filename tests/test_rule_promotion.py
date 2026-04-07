from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from harness_starter.rule_promotion import build_rule_candidates, write_rule_candidate_report


class RulePromotionTests(unittest.TestCase):
    def test_builds_candidates_from_repeated_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            harness_state = repo_root / ".harness"
            harness_state.mkdir()
            (harness_state / "state.json").write_text(
                json.dumps(
                    {
                        "gate_failures": {
                            "unit_tests": 2,
                            "hygiene": 3,
                        },
                        "hygiene_findings": {
                            "documented_test_command_mismatch:README.md": 2,
                            "unused_harness_module:src/harness_starter/stale.py": 2,
                        },
                        "repair_runs": [],
                    }
                ),
                encoding="utf-8",
            )

            candidates = build_rule_candidates(repo_root=repo_root, threshold=2)
            codes = {candidate.code for candidate in candidates}

            self.assertIn("promote_unit_test_failure", codes)
            self.assertIn("promote_hygiene_gate", codes)
            self.assertIn("promote_docs_sync_gate", codes)
            self.assertIn("promote_dead_code_scan", codes)

    def test_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            candidates = build_rule_candidates(repo_root=repo_root, threshold=99)

            report_path = write_rule_candidate_report(candidates, repo_root=repo_root)

            self.assertTrue(report_path.exists())
            self.assertIn("No promotion candidates.", report_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
