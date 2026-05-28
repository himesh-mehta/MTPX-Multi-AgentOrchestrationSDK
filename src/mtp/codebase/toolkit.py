from __future__ import annotations

from pathlib import Path
from typing import Any

from ..protocol import ToolRiskLevel, ToolSpec
from ..runtime import RegisteredTool, ToolkitLoader

from .memory import CodebaseMemory


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


class CodebaseMemoryToolkit(ToolkitLoader):
    """Read-only codebase memory tools backed by ``.mtp/memory``."""

    def __init__(self, root: str | Path) -> None:
        self.memory = CodebaseMemory(root)

    def list_tool_specs(self) -> list[ToolSpec]:
        return [
            ToolSpec(
                "codebase.status",
                "Inspect codebase memory status for the workspace.",
                _schema({}),
                risk_level=ToolRiskLevel.READ_ONLY,
                cache_ttl_seconds=5,
            ),
            ToolSpec(
                "codebase.search",
                "Search indexed codebase memory with fuzzy and semantic matching. Returns relevant snippets and line ranges. Use `query` for the search text; `pattern` is accepted as an alias.",
                _schema({"query": {"type": "string"}, "pattern": {"type": "string"}, "limit": {"type": "integer"}}),
                risk_level=ToolRiskLevel.READ_ONLY,
            ),
            ToolSpec(
                "codebase.refresh",
                "Refresh changed files in codebase memory when memory is enabled.",
                _schema({}),
                risk_level=ToolRiskLevel.READ_ONLY,
            ),
        ]

    def load_tools(self) -> list[RegisteredTool]:
        specs = {spec.name: spec for spec in self.list_tool_specs()}

        def status() -> dict[str, Any]:
            data = self.memory.status()
            return {
                "root": str(data.root),
                "db_path": str(data.db_path),
                "enabled": data.enabled,
                "file_count": data.file_count,
                "chunk_count": data.chunk_count,
                "summary_count": data.summary_count,
                "last_scan_at": data.last_scan_at,
            }

        def search(query: str | None = None, limit: int = 20, pattern: str | None = None) -> dict[str, Any]:
            query = (query or pattern or "").strip()
            if not query:
                raise ValueError("codebase.search requires `query` (or alias `pattern`).")
            hits = self.memory.search(query, limit=limit)
            return {
                "query": query,
                "enabled": self.memory.is_enabled(),
                "count": len(hits),
                "hits": [
                    {
                        "file": hit.file,
                        "score": hit.score,
                        "start_line": hit.start_line,
                        "end_line": hit.end_line,
                        "kind": hit.kind,
                        "match": hit.match,
                        "snippet": hit.snippet,
                    }
                    for hit in hits
                ],
            }

        def refresh() -> dict[str, Any]:
            stats = self.memory.refresh_changed()
            return {
                "root": str(stats.root),
                "percent": stats.percent,
                "files_seen": stats.files_seen,
                "changed_files": stats.changed_files,
                "files_deleted": stats.files_deleted,
                "chunks_indexed": stats.chunks_indexed,
            }

        return [
            RegisteredTool(spec=specs["codebase.status"], handler=status),
            RegisteredTool(spec=specs["codebase.search"], handler=search),
            RegisteredTool(spec=specs["codebase.refresh"], handler=refresh),
        ]
