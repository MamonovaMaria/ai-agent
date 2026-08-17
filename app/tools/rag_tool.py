"""Инструменты RAG для агента."""
from langchain.tools import tool
from app.rag.retriever import RAGRetriever
from app.tools.utils import log_tool_call

_rag = RAGRetriever()

@tool
@log_tool_call
def index_bookmarks(path: str = "bookmarks.html") -> str:
    """Индексирует закладки (названия и URL)."""
    result = _rag.index(path, download=False)  # без скачивания
    return f"Проиндексировано {result['indexed']} из {result['total']}"

@tool
@log_tool_call
def index_bookmarks_full(path: str = "bookmarks.html") -> str:
    """Индексирует закладки вместе с содержимым сайтов (медленно)."""
    result = _rag.index(path, download=True)
    return f"Проиндексировано {result['indexed']} из {result['total']} (скачано: {result['downloaded']})"

@tool
@log_tool_call
def search_bookmarks(query: str) -> str:
    """Ищет в закладках по запросу."""
    ctx = _rag.context(query)
    return ctx if ctx else "Ничего не найдено."
