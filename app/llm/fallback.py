from langchain_openai import ChatOpenAI

from app.config import Config


class FallbackLLM(ChatOpenAI):
    """LLM с fallback на резервную модель."""
    
    primary_model: str = Config.primary_model
    fallback_model: str = Config.fallback_model
    current_model: str = Config.primary_model
    model: str = Config.primary_model

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

    def _is_recoverable(self, error: str) -> bool:
        recoverable = [
            "rate_limit", "overloaded", "server_error",
            "503", "502", "500",
            "timeout", "unavailable", "capacity",
            "not a valid model",  # несуществующая модель
            "not found",  # 404
            "invalid_request",  # 400
        ]
        return any(msg in error.lower() for msg in recoverable)

    def switch_model(self, model_name: str) -> bool:
        self._current_model = model_name
        object.__setattr__(self, 'model_name', model_name)
        print(f"🔄 Модель переключена на: {model_name}")
        return True

    def get_current_model(self) -> str:
        return self.current_model
