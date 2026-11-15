"""Workspace boundary, .vader context and safe file operations."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


class WorkspaceError(ValueError):
    pass


class WorkspaceManager:
    SKIP_DIRS = {".git", ".agent_sessions", ".venv", "__pycache__", "node_modules", ".pytest_cache"}

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.lock = Lock()

    def safe_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise WorkspaceError("Ścieżka wychodzi poza katalog workspace")
        return candidate

    def open(self, relative_path: str = ".") -> dict[str, Any]:
        folder = self.safe_path(relative_path)
        if not folder.is_dir():
            raise WorkspaceError(f"Katalog nie istnieje: {relative_path}")
        vader = folder / ".vader"
        with self.lock:
            if vader.exists():
                try:
                    context = json.loads(vader.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    context = {"notes": vader.read_text(encoding="utf-8")}
            else:
                context = {"notes": "", "structure": [], "important_files": []}
            context["workspace"] = str(folder.relative_to(self.root) or ".")
            context["structure"] = self.structure(folder)
            context["updated_at"] = self.now()
            self._write_json(vader, context)
        return context

    def structure(self, folder: Path) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for item in sorted(folder.rglob("*")):
            if any(part in self.SKIP_DIRS for part in item.parts):
                continue
            rel = str(item.relative_to(folder)).replace(os.sep, "/")
            # The model is an infrastructure asset, not a project file to edit.
            if item.is_file() and item.suffix.lower() == ".gguf":
                continue
            if item.is_dir():
                entries.append({"path": rel, "kind": "directory"})
            else:
                entries.append({"path": rel, "kind": "file", "size": item.stat().st_size})
        return entries

    def read(self, relative_path: str) -> str:
        path = self.safe_path(relative_path)
        if not path.is_file():
            raise WorkspaceError(f"Plik nie istnieje: {relative_path}")
        return path.read_text(encoding="utf-8")

    def write(self, relative_path: str, content: str) -> None:
        path = self.safe_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.touch_vader(path.parent)

    def patch(self, relative_path: str, find: str, replace: str) -> None:
        content = self.read(relative_path)
        if find not in content:
            raise WorkspaceError("Nie znaleziono tekstu do zmiany")
        self.write(relative_path, content.replace(find, replace, 1))

    def touch_vader(self, folder: Path) -> None:
        current = self.open(str(folder.relative_to(self.root)))
        self._write_json(folder / ".vader", current)

    def save_session_context(self, session_id: str, context: dict[str, Any]) -> None:
        folder = self.safe_path(f".agent_sessions/{session_id}")
        folder.mkdir(parents=True, exist_ok=True)
        self._write_json(folder / ".vader", context)
        self.touch_vader(self.root)

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()
