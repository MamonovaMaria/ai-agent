from langchain_openai import ChatOpenAI

from app.config import Config


class FallbackLLM(ChatOpenAI):
    """LLM с fallback на резервную модель."""

    primary_model: str = Config.primary_model
    fallback_model: str = Config.fallback_model
    current_model: str = Config.primary_model
    model: str = Config.primary_model
    last_token_usage: dict = {}

    def __init__(self, **kwargs):
        super().__init__(
            base_url=Config.openrouter_base,
            api_key=Config.openrouter_key,
            model=Config.primary_model,
            temperature=0.7,
            default_headers={"HTTP-Referer": "localhost", "X-Title": "AI Agent"},
            **kwargs,
        )
        self._current_model = Config.primary_model

    def invoke(self, *args, **kwargs):
        """Перехват ответа для извлечения token usage."""
        response = super().invoke(*args, **kwargs)

        usage = {}
        if response and hasattr(response, 'response_metadata'):
            meta = response.response_metadata or {}
            usage = meta.get("token_usage") or {}

        object.__setattr__(self, 'last_token_usage', usage)
        return response

    def _is_recoverable(self, error: str) -> bool:
        recoverable = [
            "rate_limit", "overloaded", "server_error",
            "503", "502", "500",
            "timeout", "unavailable", "capacity",
            "not a valid model",
            "not found",
            "invalid_request",
        ]
        return any(msg in error.lower() for msg in recoverable)

    def switch_model(self, model_name: str) -> bool:
        self._current_model = model_name
        object.__setattr__(self, 'model_name', model_name)
        print(f"🔄 Модель переключена на: {model_name}")
        return True

    def get_current_model(self) -> str:
        return self._current_model
