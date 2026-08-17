import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_base = "https://openrouter.ai/api/v1"
    primary_model = os.getenv("PRIMARY_MODEL", "openai/gpt-4o-mini")
    fallback_model = os.getenv("FALLBACK_MODEL", "anthropic/claude-3-haiku")
    weather_key = os.getenv("OPENWEATHER_API_KEY", "")
    slack_token = os.getenv("SLACK_BOT_TOKEN", "")
    verbose = os.getenv("VERBOSE", "true").lower() == "true"  # для отображения промежуточных рассуждений
    max_iterations = int(os.getenv("MAX_ITERATIONS", "15"))
    max_execution_time = int(os.getenv("MAX_EXECUTION_TIME", "120"))
