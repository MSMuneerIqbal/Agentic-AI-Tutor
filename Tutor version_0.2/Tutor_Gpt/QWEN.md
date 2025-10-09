
# 🧠 Qwen Agent System — Step 1 (Tutor Agent + Tavily MCP)

## 🎯 Goal

Build the **base Agentic System** where the **Tutor Agent** connects to **Tavily MCP** for fetching **live educational content** and news related to the student’s lessons and interests.

---

## 🧩 System Components (for now)

1. **Tutor Agent**

   * Main agent that interacts with students.
   * Uses **Tavily MCP** to fetch **live information** (e.g., news, facts, topic updates).
   * Builds curiosity and learning interest.
   * Model: `gemini-2.5-flash`

2. **Tavily MCP**

   * Used as external knowledge retriever.
   * Replaces all other Tavily files (`tavily.py`, etc.)
   * Only connected through the Tutor Agent.

3. **Database (Basic setup)**

   * **MySQL** → store user data (name, age, subject, etc.)
   * **Redis** → store session data (conversation state, memory)
   * *(We’ll connect them later — not in this step.)*

---

## 🚀 Main Rule for Future Development

**Main Point:** Whenever you create **Specs**, **Plans**, or **Tasks**, **use MCP first** —
see which tools or ideas are new in the industry.

When you’re coding:

* In **backend** → use **Context7** and **Tavily MCP**
* In **frontend** → use **all three MCP tools**

---

## 🔧 What to Build in Step 1

✅ Focus only on **Agents Flow**
❌ No RAG yet
❌ No other MCPs
❌ No Subagents (for now)

So:

* Create the **Tutor Agent** with **Tavily MCP** connection.
* Make sure agent can **fetch and explain live info**.
* Code is clean and only uses:

  * `agents` SDK
  * `tavily MCP`
  * `asyncio`, `dotenv`

---

## 🧱 Example Code (main.py)

```python
import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, set_tracing_export_api_key
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

load_dotenv()

# LLM provider setup
provider = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=provider
)

set_tracing_export_api_key("OPENAI_API_KEY")

# Tavily MCP setup
SERVER_URL = "https://mcp.tavily.com/mcp/?tavilyApiKey=ADD_YOUR_TAVILY_KEY_HERE"
mcp_params = MCPServerStreamableHttpParams(url=SERVER_URL)

async def main_code():
    async with MCPServerStreamableHttp(params=mcp_params, name="Tutor Agent Client") as tutor_mcp:
        print("Connected to MCP server:", tutor_mcp.name)

        tutor_agent = Agent(
            name="Tutor Agent",
            instructions="You are a Tutor Agent. Use Tavily MCP to fetch live educational data for students.",
            mcp_servers=[tutor_mcp],
            model=model
        )

        result = await Runner.run(
            tutor_agent,
            "Find the latest AI education news from Pakistan"
        )
        print("RESULT:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main_code())
```

---

## ⚙️ Step Rules

1. Complete **Tutor Agent + Tavily MCP** connection first.
2. Test live data fetching works properly.
3. Once confirmed, move to:

   * Step 2 → Add Student Agent + MySQL/Redis
   * Step 3 → Add Subagents
