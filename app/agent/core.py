from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.config import Config
from app.tools import ALL_TOOLS
from app.memory.store import MemoryStore
from app.rag.retriever import RAGRetriever
import time

PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Answer in Russian. Use tools when you need real data."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


class Agent:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=Config.openrouter_base,
            api_key=Config.openrouter_key,
            model=Config.primary_model,
            temperature=0.7,
            default_headers={"HTTP-Referer": "localhost", "X-Title": "AI Agent"},
        )
        self.tools = ALL_TOOLS
        self.memory = MemoryStore()
        self.rag = RAGRetriever()

        agent = create_tool_calling_agent(self.llm, self.tools, PROMPT)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory.memory,
            verbose=Config.verbose,
            handle_parsing_errors=True,
            max_iterations=Config.max_iterations,
            max_execution_time=120,
        )

    def chat(self, message: str) -> dict:
        start = time.time()
        rag_ctx = self.rag.context(message)
        full_input = f"{rag_ctx}\n\n{message}" if rag_ctx else message
        result = self.executor.invoke({"input": full_input})
        return {"response": result["output"], "duration": time.time() - start}

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
            if msg.startswith("/index"):
                n = self.index(msg[7:].strip() or "bookmarks.html")
                print(f"✅ {n} закладок");
                continue
            print("🤖 ", end="", flush=True)
            r = self.chat(msg)
            print(r["response"])
            if r["duration"]: print(f"   ⏱️ {r['duration']:.1f}с\n")
