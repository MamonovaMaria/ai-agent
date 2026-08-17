# app/middleware/tracked_summarization.py

from deepagents.middleware import SummarizationMiddleware
from deepagents.backends import StateBackend


class TrackedSummarizationMiddleware(SummarizationMiddleware):
    """SummarizationMiddleware с отслеживанием токенов."""

    def __init__(self, model, **kwargs):
        super().__init__(
            model=model,
            backend=StateBackend(),
            **kwargs,
        )
        self.tokens_before = 0
        self.tokens_after = 0
        self.summarizations_count = 0

    def wrap_model_call(self, func):
        """Обёртка вокруг вызова модели."""

        def wrapper(state, runtime=None, *args, **kwargs):
            # До вызова
            messages = state.get("messages", []) if isinstance(state, dict) else []
            self.tokens_before = sum(
                len(str(getattr(m, 'content', '')).split()) for m in messages
            )

            # Вызов оригинальной функции с runtime
            if runtime:
                result = func(state, runtime, *args, **kwargs)
            else:
                result = func(state, *args, **kwargs)

            # После вызова
            if hasattr(result, 'content'):
                self.tokens_after = len(str(result.content).split())
            elif isinstance(result, dict) and 'messages' in result:
                msgs = result['messages']
                self.tokens_after = sum(
                    len(str(getattr(m, 'content', '')).split()) for m in msgs
                )

            if self.tokens_before > self.tokens_after and self.tokens_before > 0:
                self.summarizations_count += 1
                print(f"\n   📝 Сжатие: {self.tokens_before} → {self.tokens_after} токенов")

            return result

        return wrapper

    def get_stats(self):
        return {
            "summarizations": self.summarizations_count,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
        }