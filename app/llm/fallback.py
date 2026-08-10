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
    
    def invoke(self, *args, **kwargs):
        try:
            return super().invoke(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            if self.model != self.fallback_model and self._is_recoverable(error_msg):
                print(f"⚠️ Основная модель недоступна: {error_msg[:100]}")
                print(f"🔄 Переключаюсь на резервную: {self.fallback_model}")
                self.model = self.fallback_model
                self.current_model = self.fallback_model
                return super().invoke(*args, **kwargs)
            raise
    
    def _is_recoverable(self, error: str) -> bool:
        recoverable = ["rate_limit", "overloaded", "server_error", "503", "502", "timeout", "unavailable", "capacity"]
        return any(msg in error.lower() for msg in recoverable)
    
    def switch_model(self, model_name: str) -> bool:
        self.model = model_name
        self.current_model = model_name
        print(f"🔄 Модель переключена на: {model_name}")
        return True
    
    def get_current_model(self) -> str:
        return self.current_model
