"""Векторная БД на FAISS."""
import json
import numpy as np
from pathlib import Path
import faiss


class VectorDB:
    def __init__(self, storage_dir: str = "data/vector_db"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.dimension = 768  # nomic-embed-text
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self._load()

    def add(self, texts: list, metadatas: list = None) -> int:
        from app.rag.embedder import Embedder

        if not texts:
            return 0

        embedder = Embedder()
        metadatas = metadatas or [{}] * len(texts)

        for text, meta in zip(texts, metadatas):
            try:
                embedding = embedder.embed(text)
                self.index.add(np.array([embedding], dtype=np.float32))
                self.documents.append({"content": text, "metadata": meta})
            except Exception as e:
                print(f"⚠️ Пропущен: {e}")
                continue

        self._save()
        return len(self.documents)

    def search(self, query: str, k: int = 5) -> list:
        from app.rag.embedder import Embedder

        if self.index.ntotal == 0:
            return []

        embedder = Embedder()
        query_vec = embedder.embed(query)

        distances, indices = self.index.search(
            np.array([query_vec], dtype=np.float32), k
        )

        docs = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                docs.append(self.documents[idx])

        return docs

    def count(self) -> int:
        return self.index.ntotal

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self._save()

    def _save(self):
        faiss.write_index(self.index, str(self.storage_dir / "index.faiss"))
        with open(self.storage_dir / "docs.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    def _load(self):
        index_path = self.storage_dir / "index.faiss"
        docs_path = self.storage_dir / "docs.json"

        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
        if docs_path.exists():
            with open(docs_path, "r", encoding="utf-8") as f:
                self.documents = json.load(f)
