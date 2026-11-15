from __future__ import annotations

import chromadb


class RAGStore:
    def __init__(self, host: str, port: int):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection("workspace_knowledge")

    def search(self, query: str, limit: int = 5) -> list[str]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(query_texts=[query], n_results=limit)
        return result.get("documents", [[]])[0]

    def add(self, document_id: str, text: str, metadata: dict | None = None) -> None:
        self.collection.upsert(
            ids=[document_id], documents=[text], metadatas=[metadata or {}]
        )
