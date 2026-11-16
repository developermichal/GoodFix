from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
import psutil

from .graphchain import GraphChain, GraphState
from .models import ChatRequest, ChatResponse, FilePatchRequest, FileWriteRequest, SessionCreate, ToolCall
from .rag import RAGStore
from .workspace import WorkspaceError, WorkspaceManager

app = FastAPI(title="GoodFix GraphChain Agent", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
workspace = WorkspaceManager(os.getenv("WORKSPACE_ROOT", "/workspace"))
model_url = os.getenv("MODEL_SERVER_URL", "http://model-server:8000")
model_name = os.getenv("MODEL_SERVER_MODEL", "model")
rag = RAGStore(os.getenv("CHROMA_HOST", "chroma"), int(os.getenv("CHROMA_PORT", "8000")))
sessions: dict[str, dict[str, Any]] = {}


def system_metrics() -> dict[str, Any]:
    memory = psutil.virtual_memory()
    result: dict[str, Any] = {
        "ram_total_gb": round(memory.total / 1024**3, 2),
        "ram_available_gb": round(memory.available / 1024**3, 2),
        "ram_used_percent": memory.percent,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "disk_free_gb": round(shutil.disk_usage(workspace.root).free / 1024**3, 2),
        "gpu": [],
    }
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=2, check=True
        )
        for line in completed.stdout.splitlines():
            name, used, total, utilization, temperature = [part.strip() for part in line.split(",")]
            result["gpu"].append({"name": name, "memory_used_mb": int(used), "memory_total_mb": int(total),
                                  "utilization_percent": int(utilization), "temperature_c": int(temperature)})
    except (FileNotFoundError, subprocess.SubprocessError, ValueError):
        result["gpu_status"] = "nvidia-smi niedostępne w kontenerze"
    return result


def error(error: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(error))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/settings")
def public_settings() -> dict[str, Any]:
    """Return non-secret runtime settings for the UI."""
    return {
        "model": os.getenv("MODEL_SERVER_MODEL", "model"),
        "model_server_url": model_url,
        "context_tokens": int(os.getenv("N_CTX", "8192")),
        "gpu_layers": os.getenv("N_GPU_LAYERS", "all"),
        "tensor_split": os.getenv("TENSOR_SPLIT", "0.5,0.5"),
        "autosave_seconds": int(os.getenv("SESSION_AUTOSAVE_SECONDS", "120")),
        "workspace": os.getenv("WORKSPACE_ROOT", "/workspace"),
        "chroma": f"{os.getenv('CHROMA_HOST', 'chroma')}:{os.getenv('CHROMA_PORT', '8000')}",
        "metrics": system_metrics(),
        "rag": rag.stats(),
    }


@app.get("/api/observability/{session_id}")
def observability(session_id: str) -> dict[str, Any]:
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesja nie istnieje")
    return {"trace": session.get("trace", []), "metrics": system_metrics(), "rag": rag.stats()}


@app.post("/api/sessions")
def create_session(request: SessionCreate) -> dict[str, Any]:
    try:
        context = workspace.open(request.workspace)
    except WorkspaceError as exc:
        raise error(exc)
    session_id = request.session_id or uuid.uuid4().hex
    saved = workspace.safe_path(f".agent_sessions/{session_id}/.vader")
    if request.session_id and saved.exists():
        saved_context = json.loads(saved.read_text(encoding="utf-8"))
        context.update(saved_context)
    sessions[session_id] = {"id": session_id, "context": context, "messages": context.get("messages", [])}
    sessions[session_id]["trace"] = context.get("trace", [])
    return {"session_id": session_id, "context": context}


@app.get("/api/sessions")
def list_sessions() -> list[dict[str, Any]]:
    return [{"session_id": p.name} for p in (workspace.root / ".agent_sessions").glob("*") if p.is_dir()]


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    path = workspace.safe_path(f".agent_sessions/{session_id}/.vader")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Sesja nie istnieje")
    return {"session_id": session_id, "context": json.loads(path.read_text(encoding="utf-8"))}


@app.get("/api/tree")
def tree(path: str = ".") -> list[dict[str, Any]]:
    try:
        return workspace.structure(workspace.safe_path(path))
    except WorkspaceError as exc:
        raise error(exc)


@app.get("/api/file")
def read_file(path: str) -> dict[str, str]:
    try:
        return {"path": path, "content": workspace.read(path)}
    except WorkspaceError as exc:
        raise error(exc)


@app.post("/api/file")
def write_file(request: FileWriteRequest) -> dict[str, str]:
    try:
        workspace.write(request.path, request.content)
        return {"status": "saved", "path": request.path}
    except WorkspaceError as exc:
        raise error(exc)


@app.patch("/api/file")
def patch_file(request: FilePatchRequest) -> dict[str, str]:
    try:
        workspace.patch(request.path, request.find, request.replace)
        return {"status": "patched", "path": request.path}
    except WorkspaceError as exc:
        raise error(exc)


@app.post("/api/knowledge/pdf")
async def add_pdf(file: UploadFile = File(...)) -> dict[str, Any]:
    data = await file.read()
    temp = Path("/tmp") / f"{uuid.uuid4().hex}.pdf"
    temp.write_bytes(data)
    text = "\n".join(page.extract_text() or "" for page in PdfReader(str(temp)).pages)
    chunks = [text[i : i + 3000] for i in range(0, len(text), 3000)]
    for index, chunk in enumerate(chunks):
        rag.add(f"{file.filename}-{index}", chunk, {"filename": file.filename, "type": "pdf"})
    temp.unlink(missing_ok=True)
    return {"filename": file.filename, "chunks": len(chunks)}


async def call_model(messages: list[dict[str, str]]) -> tuple[str, dict[str, int]]:
    async with httpx.AsyncClient(timeout=300) as client:
        response = await client.post(
            f"{model_url}/v1/chat/completions",
            json={"model": model_name, "messages": messages, "temperature": 0.2},
        )
        response.raise_for_status()
        payload = response.json()
        usage = payload.get("usage") or {}
        if not usage:
            prompt_tokens = sum(max(1, len(item["content"]) // 4) for item in messages)
            completion = payload["choices"][0]["message"]["content"]
            usage = {"prompt_tokens": prompt_tokens, "completion_tokens": max(1, len(completion) // 4),
                     "total_tokens": prompt_tokens + max(1, len(completion) // 4), "estimated": 1}
        return payload["choices"][0]["message"]["content"], {key: int(value) for key, value in usage.items() if isinstance(value, (int, float))}


def extract_actions(answer: str) -> list[dict[str, Any]]:
    """Odczytaj opcjonalne akcje JSON bez wykonywania kodu z odpowiedzi modelu."""
    try:
        payload = json.loads(answer)
    except json.JSONDecodeError:
        return []
    return payload.get("actions", []) if isinstance(payload, dict) else []


def execute_actions(actions: list[dict[str, Any]]) -> list[ToolCall]:
    calls: list[ToolCall] = []
    for action in actions:
        name = action.get("name", "")
        arguments = action.get("arguments", {})
        try:
            if name == "write_file":
                workspace.write(arguments["path"], arguments["content"])
                result = "zapisano plik"
            elif name == "patch_file":
                workspace.patch(arguments["path"], arguments["find"], arguments["replace"])
                result = "zmieniono plik"
            elif name == "read_file":
                result = workspace.read(arguments["path"])
            elif name == "list_tree":
                result = json.dumps(workspace.structure(workspace.safe_path(arguments.get("path", "."))), ensure_ascii=False)
            else:
                result = "nieznana akcja"
        except (KeyError, WorkspaceError) as exc:
            result = f"błąd: {exc}"
        calls.append(ToolCall(name=name, arguments=arguments, result=result[:4000]))
    return calls


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    session = sessions.get(request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Sesja nie istnieje")
    trace: list[dict[str, Any]] = []
    state = GraphState({"request": request.message, "session": session, "rag": [], "answer": "", "token_usage": {}})
    graph = GraphChain()
    def rag_node(s: GraphState) -> None:
        started = time.perf_counter(); s.values["rag"] = rag.search(s.values["request"])
        trace.append({"step": "rag_search", "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                      "details": {"results": len(s.values["rag"])}})
    graph.add("rag_search", rag_node)

    async def model_node(s: GraphState) -> None:
        context = json.dumps(s.values["session"]["context"], ensure_ascii=False)
        prompt = f"Workspace context (.vader): {context}\nRAG: {s.values['rag']}\n" \
            "Jeśli trzeba zmienić pliki, odpowiedz wyłącznie JSON-em: " \
            "{\"answer\":\"opis\",\"actions\":[{\"name\":\"write_file|patch_file|read_file|list_tree\",\"arguments\":{}}]}. " \
            "Ścieżki są względne wobec workspace."
        started = time.perf_counter()
        s.values["answer"], s.values["token_usage"] = await call_model([
            {"role": "system", "content": "Jesteś aktywnym agentem programistycznym. Pracujesz wyłącznie w workspace."},
            {"role": "system", "content": prompt},
            {"role": "user", "content": s.values["request"]},
        ])
        trace.append({"step": "model", "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                      "details": {**s.values["token_usage"], "tokens_per_second": round(
                          s.values["token_usage"].get("completion_tokens", 0) / max(time.perf_counter() - started, 0.001), 2)}})

    graph.add("model", model_node)
    await graph.run(state)
    raw_answer = state.values["answer"]
    action_calls = execute_actions(extract_actions(raw_answer))
    trace.append({"step": "actions", "duration_ms": 0, "details": {"count": len(action_calls),
                                                                        "names": [call.name for call in action_calls]}})
    try:
        parsed = json.loads(raw_answer)
        answer = parsed.get("answer", raw_answer) if isinstance(parsed, dict) else raw_answer
    except json.JSONDecodeError:
        answer = raw_answer
    session["messages"].extend([{"role": "user", "content": request.message}, {"role": "assistant", "content": answer}])
    session["context"]["messages"] = session["messages"][-20:]
    session.setdefault("trace", []).append({"at": time.time(), "request": request.message, "steps": trace,
                                             "token_usage": state.values["token_usage"]})
    session["trace"] = session["trace"][-50:]
    session["context"]["trace"] = session["trace"]
    workspace.save_session_context(request.session_id, session["context"])
    return ChatResponse(answer=answer, tool_calls=action_calls, rag_count=len(state.values["rag"]), session_id=request.session_id,
                        trace=trace, token_usage=state.values["token_usage"])


async def autosave() -> None:
    while True:
        await asyncio.sleep(int(os.getenv("SESSION_AUTOSAVE_SECONDS", "120")))
        for session_id, session in sessions.items():
            workspace.save_session_context(session_id, session["context"])


@app.on_event("startup")
async def startup() -> None:
    asyncio.create_task(autosave())
