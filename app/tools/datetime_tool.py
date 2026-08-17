from langchain.tools import tool
from datetime import datetime

from app.tools.utils import log_tool_call


@tool
@log_tool_call
def get_datetime() -> str:
    """Текущие дата, время, день недели."""
    now = datetime.now()
    days = ["пн","вт","ср","чт","пт","сб","вс"]
    return f"{now:%Y-%m-%d %H:%M}, {days[now.weekday()]}, нед {now.isocalendar()[1]}"
