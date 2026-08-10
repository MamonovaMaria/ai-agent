import json, numpy as np
from pathlib import Path


class VectorDB:
    def __init__(self, path: str = "data/vector_db"):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.docs = []
        self.vecs = []
        self._load()

    def add(self, doc: dict, vec: list):
        self.docs.append(doc)
        self.vecs.append(vec)
        self._save()

    def search(self, query_vec: list, top_k: int = 5) -> list:
        if not self.vecs: return []
        v = np.array(self.vecs)
        q = np.array(query_vec)
        sim = np.dot(v, q) / (np.linalg.norm(v, axis=1) * np.linalg.norm(q) + 1e-8)
        idx = np.argsort(sim)[-top_k:][::-1]
        return [(self.docs[i], float(sim[i])) for i in idx if sim[i] > 0.3]

    def _save(self):
        with open(self.path / "docs.json", "w", encoding="utf-8") as f:
            json.dump(self.docs, f, ensure_ascii=False)
        if self.vecs: np.save(self.path / "vecs.npy", np.array(self.vecs))

    def _load(self):
        if (self.path / "docs.json").exists():
            with open(self.path / "docs.json", "r", encoding="utf-8") as f:
                self.docs = json.load(f)
        if (self.path / "vecs.npy").exists():
            self.vecs = np.load(self.path / "vecs.npy").tolist()
