"""Minimalny graf wykonawczy agenta: context -> RAG -> model -> action -> persist."""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Awaitable, Callable


@dataclass
class GraphState:
    values: dict[str, Any] = field(default_factory=dict)


class GraphChain:
    def __init__(self):
        self.nodes: list[tuple[str, Callable[[GraphState], Any]]] = []

    def add(self, name: str, node: Callable[[GraphState], None]) -> "GraphChain":
        self.nodes.append((name, node))
        return self

    async def run(self, state: GraphState) -> GraphState:
        for name, node in self.nodes:
            state.values["active_node"] = name
            result = node(state)
            if inspect.isawaitable(result):
                await result
        return state
