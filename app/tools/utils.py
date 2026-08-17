"""Базовый декоратор для инструментов."""
from functools import wraps
from langchain.tools import tool

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"


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
        print(f"{YELLOW}\n🔧 Вызван инструмент: {func.__name__}")
        print(f"   Аргументы: {kwargs if kwargs else args}")
        result = func(*args, **kwargs)
        print(f"   Результат: {str(result)[:100]}...\n{RESET}")
        return result
    return wrapper
