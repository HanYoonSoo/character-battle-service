from __future__ import annotations

import re
from pathlib import Path

from harness_starter.models import ContextChunk


class ProjectMemory:
    def __init__(
        self,
        docs_root: Path,
        global_constraints: list[str] | None = None,
    ) -> None:
        self.docs_root = docs_root
        self.global_constraints = global_constraints or []
        self._document_cache: dict[Path, tuple[int, str]] = {}

    def get_global_constraints(self) -> list[str]:
        return list(self.global_constraints)

    def get_relevant_context(self, current_task: str, limit: int = 3) -> list[ContextChunk]:
        query_terms = self._tokenize(current_task)
        scored_chunks: list[ContextChunk] = []
        all_chunks: list[ContextChunk] = []

        for path in sorted(self.docs_root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
                continue
            text = self._read_document(path)
            chunk = ContextChunk(
                source=path.relative_to(self.docs_root).as_posix(),
                text=text.strip(),
                score=0,
            )
            all_chunks.append(chunk)
            score = self._score_text(text, query_terms)
            if score > 0:
                scored_chunks.append(
                    ContextChunk(
                        source=chunk.source,
                        text=chunk.text,
                        score=score,
                    )
                )

        scored_chunks.sort(key=lambda chunk: chunk.score, reverse=True)
        if scored_chunks:
            return scored_chunks[:limit]
        return all_chunks[:limit]

    def run_garbage_collection(self) -> int:
        valid_paths = {
            path.resolve()
            for path in self.docs_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".txt"}
        }
        stale_paths = [
            path for path in self._document_cache
            if path not in valid_paths
        ]
        for path in stale_paths:
            del self._document_cache[path]
        return len(stale_paths)

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z0-9_/-]+", text.lower()) if len(token) > 2}

    @classmethod
    def _score_text(cls, text: str, query_terms: set[str]) -> int:
        if not query_terms:
            return 0
        lowered = text.lower()
        return sum(1 for term in query_terms if term in lowered)

    def _read_document(self, path: Path) -> str:
        resolved_path = path.resolve()
        mtime_ns = path.stat().st_mtime_ns
        cached = self._document_cache.get(resolved_path)
        if cached is not None and cached[0] == mtime_ns:
            return cached[1]

        text = path.read_text(encoding="utf-8")
        self._document_cache[resolved_path] = (mtime_ns, text)
        return text
