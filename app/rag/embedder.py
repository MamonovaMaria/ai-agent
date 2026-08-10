import ollama


class Embedder:
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model

    def embed(self, text: str) -> list:
        return ollama.embeddings(model=self.model, prompt=text)["embedding"]
