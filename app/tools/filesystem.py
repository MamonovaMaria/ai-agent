from langchain.tools import tool
from pathlib import Path

from app.tools.utils import log_tool_call


@tool
@log_tool_call
def read_file(path: str) -> str:
    """Читает файл или показывает содержимое директории."""
    p = Path(path)
    if not p.exists(): return f"Не найден: {path}"
    if p.is_dir():
        items = []
        for x in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name)):
            icon = "📁" if x.is_dir() else "📄"
            items.append(f"  {icon} {x.name}")
        return "\n".join(items[:30])
    c = p.read_text("utf-8")
    return f"```{p.suffix[1:]}\n{c[:3000]}\n```"

@tool
@log_tool_call
def count_files(directory: str = ".", extension: str = "") -> str:
    """Подсчёт файлов в директории."""
    p = Path(directory)
    if not p.exists(): return f"Не найден: {directory}"
    files = [f for f in p.rglob("*") if f.is_file() and (not extension or f.suffix==extension)]
    return f"Файлов: {len(files)}"

@tool
@log_tool_call
def create_file(path: str, content: str = "") -> str:
    """Создаёт файл."""
    p = Path(path)
    if p.exists(): return f"Существует: {path}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, "utf-8")
    return f"Создан: {path} ({len(content)} симв)"
