"""Эмбеддинги через Ollama."""
import ollama

from app.config import Config


class Embedder:
    def __init__(self, model: str = "nomic-embed-text", host: str = Config.ollama_host):
        self.model = model
        self.client = ollama.Client(host=host)

    def embed(self, text: str) -> list:
        response = self.client.embeddings(model=self.model, prompt=text)
        return response["embedding"]
    