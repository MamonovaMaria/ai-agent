import time

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware import SummarizationMiddleware
from langchain_core.messages import HumanMessage

from app.config import Config
from app.llm import FallbackLLM
from app.memory.persistent_store import PersistentMemory
from app.rag.retriever import RAGRetriever
from app.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are a helpful AI assistant. Answer in Russian.

When user asks about their bookmarks:
1. Call search_bookmarks ONCE with the user's query
2. Read the results
3. Give a summary based ONLY on those results
4. Do NOT call any other tools for bookmark questions

When user asks about weather:
- Call get_weather ONCE with the city name

When user asks about time/date:
- Call get_datetime ONCE

When user asks to read a file:
- Call read_file ONCE with the path

For other questions:
- Use the appropriate tool ONCE
- If no tool is needed, answer directly
- Do NOT call the same tool twice
- Do NOT list directories just to explore

Be concise. Use tools only when you need real data."""


class Agent:
    def __init__(self):
        self.llm = FallbackLLM()
        self.tools = ALL_TOOLS
        self.memory = PersistentMemory()
        self.rag = RAGRetriever()

        # SummarizationMiddleware — сжимает историю автоматически
        self.summarization = SummarizationMiddleware(
            model=self.llm,
            backend=StateBackend(),
            max_tokens_before_summary=2000,
            max_tokens_after_summary=500,
        )

        self.executor = self._create_executor()

    def _create_executor(self):
        return create_deep_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=SYSTEM_PROMPT,
            middleware=[self.summarization],
            checkpointer=self.memory.checkpointer,
        )

    def chat(self, message: str) -> dict:
        start = time.time()
        rag_ctx = self.rag.context(message) or ""
        full_message = f"{rag_ctx}\n\n{message}" if rag_ctx else message

        try:
            result = self.executor.invoke(
                {"messages": [HumanMessage(content=full_message)]},
                config={"configurable": {"thread_id": self.memory.thread_id}},
            )

            output = result["messages"][-1].content
            return {"response": output, "duration": time.time() - start}
        except Exception as e:
            error_msg = str(e)
            if self.llm.model != self.llm.fallback_model:
                print(f"⚠️ Ошибка: {error_msg[:100]}")
                self.llm.switch_model(self.llm.fallback_model)
                self.executor = self._create_executor()
                try:
                    result = self.executor.invoke(
                        {"messages": [HumanMessage(content=full_message)]},
                        config={"configurable": {"thread_id": self.memory.thread_id}},
                    )
                    output = result["messages"][-1].content
                    return {"response": output, "duration": time.time() - start}
                except Exception as e2:
                    return {"response": f"❌ {str(e2)[:200]}", "duration": time.time() - start}
            return {"response": f"❌ {error_msg[:200]}", "duration": time.time() - start}

    def run_console(self):
        print(f"🤖 Модель: {Config.primary_model}\n")
        while True:
            try:
                msg = input("👤 Вы: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋")
                break
            if not msg: continue
            if msg in ("выход", "exit"): print("👋"); break
            if msg.startswith("/model ") or msg.startswith("переключись на модель "):
                new_model = msg[7:].strip() if msg.startswith("/model ") else msg[len("переключись на модель "):].strip()
                if self.llm.switch_model(new_model):
                    self.executor = self._create_executor()
                    print(f"✅ Модель: {new_model}")
                continue
            print("🤖 ", end="", flush=True)
            r = self.chat(msg)
            print(r["response"])
            if r["duration"]:
                print(f"   ⏱️ {r['duration']:.1f}с\n")
