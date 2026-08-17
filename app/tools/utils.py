"""Базовый декоратор для инструментов."""
from functools import wraps

from app.utils import ConsoleColor


def log_tool_call(func):
    """
    Декоратор, который выводит название инструмента при вызове.
    Использование:
        @tool
        @log_tool_call
        def my_tool(...): ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{ConsoleColor.YELLOW}\n🔧 Вызван инструмент: {func.__name__}")
        print(f"   Аргументы: {kwargs if kwargs else args}")
        result = func(*args, **kwargs)
        print(f"   Результат: {str(result)[:100]}...\n{ConsoleColor.RESET}")
        return result
    return wrapper
