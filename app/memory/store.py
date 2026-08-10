from langchain.memory import ConversationBufferWindowMemory


class MemoryStore:
    def __init__(self, k: int = 20):
        self.memory = ConversationBufferWindowMemory(
            k=k, memory_key="chat_history", return_messages=True, output_key="output",
        )

    def clear(self):
        self.memory.clear()
