import os
import time

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.config import Config
from app.llm import FallbackLLM
from app.memory.store import MemoryStore
from app.rag.retriever import RAGRetriever
from app.tools import ALL_TOOLS

PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant. Answer in Russian.

When user asks about their bookmarks:
1. Call search_bookmarks ONCE with the user's query
2. Read the results
3. Give a summary based ONLY on those results
4. Do NOT call any other tools for bookmark questions

For other questions, use the appropriate tool ONCE and answer."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


class Agent:
    def __init__(self):
        self.llm = FallbackLLM()
        self.tools = ALL_TOOLS
        self.memory = MemoryStore()
        self.rag = RAGRetriever()
        self.executor = self._create_executor()

    def _create_executor(self):
        agent = create_tool_calling_agent(self.llm, self.tools, PROMPT)
        return AgentExecutor(
            agent=agent, tools=self.tools, memory=self.memory.memory,
            verbose=Config.verbose, handle_parsing_errors=True,
            max_iterations=Config.max_iterations,
            max_execution_time=int(os.getenv("MAX_EXECUTION_TIME", "120")),
        )

    def chat(self, message: str) -> dict:
        start = time.time()
        rag_ctx = self.rag.context(message)
        full_input = f"{rag_ctx}\n\n{message}" if rag_ctx else message

        try:
            result = self.executor.invoke({"input": full_input})
            return {"response": result["output"], "duration": time.time() - start}
        except Exception as e:
            error_msg = str(e)
            if self.llm.model != self.llm.fallback_model:
                print(f"⚠️ Ошибка: {error_msg[:100]}")
                self.llm.switch_model(self.llm.fallback_model)
                self.executor = self._create_executor()
                try:
                    result = self.executor.invoke({"input": full_input})
                    return {"response": result["output"], "duration": time.time() - start}
                except Exception as e2:
                    return {"response": f"❌ Резервная тоже недоступна: {str(e2)[:200]}",
                            "duration": time.time() - start}
            return {"response": f"❌ {error_msg[:200]}", "duration": time.time() - start}

    def clear(self):
        self.memory.clear()

    def index(self, path: str) -> int:
        return self.rag.index(path)

    def run_console(self):
        print(f"🤖 Агент готов. Модель: {Config.primary_model}\n")
        while True:
            try:
                msg = input("👤 Вы: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋")
                break
            if not msg: continue
            if msg in ("выход", "exit"): print("👋"); break
            if msg == "/clear": self.clear(); print("✅"); continue
            if msg.startswith("/model ") or msg.startswith("переключись на модель "):
                new_model = msg[7:].strip()
                if self.llm.switch_model(new_model):
                    print(f"✅ Модель: {new_model}")
                else:
                    print("❌ Не удалось переключить модель")
                continue
            if msg.startswith("/index"):
                n = self.index(msg[7:].strip() or "bookmarks.html")
                print(f"✅ {n} закладок");
                continue
            print("🤖 ", end="", flush=True)
            r = self.chat(msg)
            print(r["response"])
            if r["duration"]: print(f"   ⏱️ {r['duration']:.1f}с\n")
