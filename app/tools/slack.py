from langchain.tools import tool
import requests
from app.config import Config

@tool
def slack_channels() -> str:
    """Каналы Slack."""
    if not Config.slack_token: return "Нет токена"
    r = requests.post("https://slack.com/api/conversations.list",
        headers={"Authorization":f"Bearer {Config.slack_token}"},
        data={"types":"public_channel"}, timeout=10)
    d = r.json()
    if not d.get("ok"): return f"Ошибка: {d.get('error')}"
    return "Slack:\n"+"\n".join(f"  • #{c['name']}" for c in d.get("channels",[])[:10])


@tool
def slack_send(channel: str, text: str) -> str:
    """Отправляет сообщение в Slack-канал. channel — название канала (например, #general), text — текст сообщения."""
    if not Config.slack_token:
        return "Токен Slack не настроен (SLACK_BOT_TOKEN)"

    r = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {Config.slack_token}"},
        data={"channel": channel, "text": text},
        timeout=10,
    )
    d = r.json()

    if not d.get("ok"):
        return f"Ошибка отправки: {d.get('error', '')}"

    return f"Сообщение отправлено в {channel}"
