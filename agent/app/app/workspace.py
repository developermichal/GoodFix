import os
from pathlib import Path
from typing import Optional, Dict, Any


class WorkspaceError(Exception):
    pass

class WorkspaceManager:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def safe_path(self, path: str) -> Path:
        full_path = self.base_path / path
        if not full_path.resolve().is_relative_to(self.base_path):
            raise WorkspaceError("Path traversal detected")
        return full_path

    def open(self, path: str, mode: str = "r") -> Any:
        safe_path = self.safe_path(path)
        return open(safe_path, mode)

    def structure(self) -> Dict[str, Any]:
        return {
            "base_path": str(self.base_path),
            "files": []
        }