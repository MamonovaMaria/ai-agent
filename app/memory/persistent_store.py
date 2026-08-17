"""Персистентное хранилище на SQLite."""
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


class PersistentMemory:
    def __init__(self, db_path: str = "data/chat_history.db"):
        import os
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.checkpointer = SqliteSaver(self.conn)
        self.thread_id = "main_thread"
