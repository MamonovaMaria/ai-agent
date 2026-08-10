"""RAG: поиск и контекст."""

import requests
import re

from app.rag.vector_db import VectorDB


class RAGRetriever:
    def __init__(self):
        self.db = VectorDB()

    def index(self, path: str = "bookmarks.html", download: bool = False) -> dict:
        from html.parser import HTMLParser

        bookmarks = []

        class P(HTMLParser):
            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    u = dict(attrs).get("href", "")
                    if u.startswith("http"):
                        self.u = u;
                        self.t = ""

            def handle_data(self, data):
                if hasattr(self, 'u'): self.t += data

            def handle_endtag(self, tag):
                if tag == "a" and hasattr(self, 'u'):
                    bookmarks.append({"title": self.t.strip(), "url": self.u})
                    del self.u

        with open(path, "r", encoding="utf-8") as f:
            P().feed(f.read())

        texts = []
        metadatas = []
        downloaded = 0

        for bm in bookmarks:
            content = f"{bm['title']}\n{bm['url']}"

            if download:
                try:
                    r = requests.get(bm["url"], headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    text = re.sub(r'<[^>]+>', ' ', r.text)
                    text = re.sub(r'\s+', ' ', text).strip()[:2000]
                    if text:
                        content = f"{bm['title']}\n{bm['url']}\n\n{text}"
                        downloaded += 1
                except Exception:
                    pass

            texts.append(content)
            metadatas.append({"title": bm["title"], "url": bm["url"], "source": "bookmarks"})

        indexed = self.db.add(texts, metadatas)
        return {"indexed": indexed, "total": len(bookmarks), "downloaded": downloaded}

    def context(self, query: str, top_k: int = 3) -> str:
        if self.db.count() == 0:
            return ""
        docs = self.db.search(query, top_k)
        if not docs:
            return ""
        lines = ["\n📚 НАЙДЕНО В ЗАКЛАДКАХ:"]
        for i, doc in enumerate(docs, 1):
            m = doc["metadata"]
            lines.append(f"{i}. {m.get('title', 'Без названия')}")
            if m.get('url'): lines.append(f"   {m['url']}")
        return "\n".join(lines)

    def clear(self):
        self.db.clear()
