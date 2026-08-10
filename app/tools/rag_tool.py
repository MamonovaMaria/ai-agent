"""Инструменты RAG для агента."""
from langchain.tools import tool
from app.rag.retriever import RAGRetriever

_rag = RAGRetriever()

@tool
def index_bookmarks(path: str = "bookmarks.html") -> str:
    """Индексирует закладки."""
    result = _rag.index(path, download=True)
    return f"Проиндексировано {result['indexed']} из {result['total']} (скачано: {result['downloaded']})"

@tool
def search_bookmarks(query: str) -> str:
    """Ищет в закладках по запросу."""
    ctx = _rag.context(query)
    return ctx if ctx else "Ничего не найдено."
