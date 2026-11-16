from typing import Any, Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    workspace: str = "."
    session_id: str | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1)


class FileWriteRequest(BaseModel):
    path: str
    content: str


class FilePatchRequest(BaseModel):
    path: str
    find: str
    replace: str


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = {}
    result: str = ""


class ChatResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCall] = []
    rag_count: int = 0
    session_id: str
    trace: list[dict[str, Any]] = []
    token_usage: dict[str, int] = {}


class FileEntry(BaseModel):
    path: str
    kind: Literal["file", "directory"]
    size: int | None = None

