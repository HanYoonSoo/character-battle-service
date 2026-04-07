from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from harness_starter.context_manager import ProjectMemory


class ProjectMemoryTests(unittest.TestCase):
    def test_returns_only_matching_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            (docs_root / "alpha.md").write_text(
                "Harness retries after validation failure.", encoding="utf-8"
            )
            (docs_root / "beta.md").write_text(
                "Unrelated inventory management note.", encoding="utf-8"
            )

            memory = ProjectMemory(docs_root=docs_root)
            chunks = memory.get_relevant_context("retry after validation failure")

            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0].source, "alpha.md")

    def test_garbage_collection_drops_deleted_cached_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_root = Path(temp_dir)
            alpha = docs_root / "alpha.md"
            alpha.write_text("Harness retries after validation failure.", encoding="utf-8")

            memory = ProjectMemory(docs_root=docs_root)
            memory.get_relevant_context("retry after validation failure")
            self.assertEqual(len(memory._document_cache), 1)

            alpha.unlink()

            removed = memory.run_garbage_collection()

            self.assertEqual(removed, 1)
            self.assertEqual(len(memory._document_cache), 0)


if __name__ == "__main__":
    unittest.main()
