from typing import List, Dict, Any
from langchain_core.documents import Document


class RAGStore:
    def __init__(self):
        self.documents = []

    def search(self, query: str) -> List[Document]:
        # Implement search logic
        return []

    def add(self, documents: List[Document]):
        self.documents.extend(documents)

    def stats(self) -> Dict[str, Any]:
        return {
            "document_count": len(self.documents)
        }