import os
import re
import subprocess

import requests
from langchain.tools import tool

from app.tools.utils import log_tool_call


@tool
@log_tool_call
def github_trending(language: str = "") -> str:
    """Популярные репозитории GitHub. Можно указать язык: python, javascript, go."""
    url = f"https://github.com/trending/{language}?since=daily" if language else "https://github.com/trending?since=daily"

    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
    except Exception as e:
        return f"Ошибка доступа к GitHub: {e}"

    repos = []
    for match in re.finditer(r'href="(/(?!trending)[^/]+/[^/"]+)"', r.text):
        parts = match.group(1).strip("/").split("/")
        if len(parts) == 2:
            repos.append(f"  • {parts[0]}/{parts[1]}")
            if len(repos) == 5:
                break

    return "Тренды GitHub:\n" + "\n".join(repos) if repos else "Не удалось найти репозитории"


@tool
@log_tool_call
def git_commit(
        message: str,
        files: str = ".",
        exclude: str = "",
) -> str:
    """
    Делает коммит в git-репозитории.

    Параметры:
    - message: сообщение коммита (обязательно)
    - files: какие файлы добавить. "." — все изменённые, или перечислить через пробел: "app/agent.py app/tools/github.py"
    - exclude: какие файлы исключить через пробел: "*.log .env"

    Примеры:
    - git_commit("обновление", ".", "")
    - git_commit("фикс", "app/agent.py", "")
    - git_commit("всё кроме логов", ".", "*.log")
    """
    repo_path = os.getenv("LOCAL_REPO_PATH", ".")

    try:
        # git add
        add_cmd = ["git", "add"] + files.split()
        result = subprocess.run(add_cmd, cwd=repo_path, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return f"Ошибка git add: {result.stderr}"

        # Исключения
        if exclude:
            for pattern in exclude.split():
                subprocess.run(
                    ["git", "reset", "--", pattern],
                    cwd=repo_path, capture_output=True, text=True, timeout=10,
                )

        # git commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path, capture_output=True, text=True, timeout=10,
        )

        if result.returncode == 0:
            return f"✅ Коммит создан:\n{result.stdout.strip()}"
        elif "nothing to commit" in (result.stdout + result.stderr):
            return "Нечего коммитить — нет изменений."
        else:
            return f"Ошибка: {result.stderr}"

    except FileNotFoundError:
        return "Git не найден"
    except Exception as e:
        return f"Ошибка: {e}"
