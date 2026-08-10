from app.rag.embedder import Embedder
from app.rag.vector_db import VectorDB
import hashlib


class RAGRetriever:
    def __init__(self):
        self.embedder = Embedder()
        self.db = VectorDB()

    def index(self, path: str = "bookmarks.html") -> int:
        from html.parser import HTMLParser
        docs = []

        class P(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    u = dict(attrs).get("href", "")
                    if u.startswith("http"): self.u = u; self.t = ""

            def handle_data(self, data):
                if hasattr(self, 'u'): self.t += data

            def handle_endtag(self, tag):
                if tag == "a" and hasattr(self, 'u'):
                    docs.append(
                        {"id": hashlib.md5(self.u.encode()).hexdigest()[:12], "title": self.t.strip(), "url": self.u,
                         "content": f"{self.t.strip()}\n{self.u}"})
                    del self.u

        with open(path, "r", encoding="utf-8") as f:
            P().feed(f.read())
        for d in docs: self.db.add(d, self.embedder.embed(d["content"]))
        return len(docs)

    def context(self, query: str, top_k: int = 3) -> str:
        if not self.db.docs: return ""
        results = self.db.search(self.embedder.embed(query), top_k)
        if not results: return ""
        return "\n📚 ЗАКЛАДКИ:\n" + "\n".join(f"{i}. {d['title']} ({s:.0%})" for i, (d, s) in enumerate(results, 1))
