# Tutor Agent — AI-Powered LMS

A general-purpose AI tutoring system. Students are assessed on their learning style (VARK), given a personalised study plan, taught any subject through a knowledge base you upload, quizzed, and given progress feedback — all through a real-time chat interface.

**Not tied to any domain.** Everything the agents teach comes from content you upload to Pinecone.

---

## What You Need Before Starting

### Accounts and API Keys

| Service | What for | Get it at |
|---|---|---|
| **OpenAI** | GPT-4o (all agents), text-embedding-3-small (RAG), web search | platform.openai.com |
| **Pinecone** | Vector database for course content | app.pinecone.io |
| **MongoDB Atlas** | Sessions, users, progress data | mongodb.com/atlas |

That's it — three services, three API keys.

### Software on Your Machine

| Tool | Minimum version | Check with |
|---|---|---|
| Python | 3.12 | `python --version` |
| Node.js | 18 | `node --version` |
| npm | 9 | `npm --version` |

---

## Setup — Step by Step

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd Sir-Project-Tutor-Agent
```

### 2. Set up the backend

```bash
cd backend

# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac / Linux:
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### 3. Create the backend `.env` file

```bash
# Copy the template
copy .env.example .env       # Windows
cp .env.example .env         # Mac / Linux
```

Open `backend/.env` and fill in your keys:

```env
# ── Required ──────────────────────────────────────────────────────
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pc-...
DATABASE_URL=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/tutor_lms

# ── Pinecone index (create this index in your Pinecone console) ───
PINECONE_INDEX_NAME=tutor-lms

# ── Leave these as defaults unless you have a reason to change ────
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:3000
```

> **Important — Pinecone index settings:**
> When creating your index in the Pinecone console, set:
> - **Dimensions:** `1536`  (matches text-embedding-3-small)
> - **Metric:** `cosine`
> - **Type:** Serverless, cloud `aws`, region `us-east-1`

### 4. Set up the frontend

```bash
cd ../frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Running the App

You need **two terminals** — one for the backend, one for the frontend.

**Terminal 1 — Backend:**

```bash
cd backend
.venv\Scripts\activate        # Windows
# or: source .venv/bin/activate

uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     MongoDB connected
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 14.x.x
- Local: http://localhost:3000
✓ Ready in Xs
```

**Open your browser:** `http://localhost:3000`

---

## Adding Course Content (Required for Teaching)

The agents teach from whatever you put in Pinecone. Without content, RAG queries will fail.

### Option A — Write a quick ingestion script

```python
import asyncio
from openai import AsyncOpenAI
from pinecone import Pinecone

openai_client = AsyncOpenAI(api_key="sk-...")
pc = Pinecone(api_key="pc-...")
index = pc.Index("tutor-lms")

async def upload_chunk(text: str, source: str, page: int, content_type: str, chunk_id: str):
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    vector = response.data[0].embedding

    index.upsert(vectors=[{
        "id": chunk_id,
        "values": vector,
        "metadata": {
            "content": text,
            "source": source,
            "page": page,
            "content_type": content_type,   # see valid values below
        }
    }])

asyncio.run(upload_chunk(
    text="Python variables are containers for storing data values...",
    source="python_intro.pdf",
    page=1,
    content_type="lesson",
    chunk_id="python_intro_p1_chunk1",
))
```

### Valid `content_type` values

| Value | Used by |
|---|---|
| `lesson`, `example`, `explanation`, `tutorial` | Tutor agent |
| `overview`, `structure`, `curriculum`, `roadmap` | Planning agent |
| `concept`, `definition`, `comparison`, `best_practice` | Assessment + Quiz agents |
| `command`, `configuration` | Quiz agent |
| `introduction` | Orchestrator |

### Option B — Use pdfplumber to batch-upload a PDF

```bash
pip install pdfplumber
```

```python
import pdfplumber, asyncio, uuid
from openai import AsyncOpenAI
from pinecone import Pinecone

openai_client = AsyncOpenAI(api_key="sk-...")
index = Pinecone(api_key="pc-...").Index("tutor-lms")

async def upload_pdf(pdf_path: str, content_type: str = "lesson"):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if len(text.strip()) < 50:
                continue
            resp = await openai_client.embeddings.create(
                model="text-embedding-3-small", input=text[:2000]
            )
            index.upsert(vectors=[{
                "id": str(uuid.uuid4()),
                "values": resp.data[0].embedding,
                "metadata": {
                    "content": text[:2000],
                    "source": pdf_path,
                    "page": i + 1,
                    "content_type": content_type,
                }
            }])
            print(f"Uploaded page {i+1}")

asyncio.run(upload_pdf("my_course_material.pdf"))
```

---

## How the App Works

### User Flow

```
Landing Page → Register / Login → Dashboard
                                     │
                                  Chat opens
                                     │
                              1. Greeting (Orchestrator)
                              2. VARK Assessment (6 questions)
                              3. Study Plan created (GPT-4o + RAG)
                              4. Lessons delivered (GPT-4o + RAG + Web)
                              5. Quizzes (GPT-4o generates questions from RAG)
                              6. Feedback on progress
```

### The 6 AI Agents

| Agent | Role |
|---|---|
| **Orchestrator** | Welcomes the student, understands their goals, routes to other agents, handles general conversation |
| **Assessment** | Runs a 6-question VARK test to detect Visual / Auditory / Reading / Kinesthetic learning style |
| **Planning** | Asks about goals and schedule, uses GPT-4o + RAG + web search to generate a structured study plan |
| **Tutor** | Teaches the topic using RAG content + live web search, adapts style to VARK, supports brainstorming |
| **Quiz** | Generates multiple-choice questions via GPT-4o from RAG content, evaluates answers, scores the student |
| **Feedback** | Analyses quiz scores, topics completed, and time spent — gives personalised coaching advice |

### Session State Machine

```
GREETING → ASSESSING → PLANNING → TUTORING ⇄ QUIZZING
```

State transitions happen automatically — when assessment ends, planning starts; when the plan is ready, tutoring begins.

### Real-time Communication

All chat goes over WebSocket at `ws://localhost:8000/ws/sessions/{session_id}`.

The frontend (`providers.tsx`) opens the connection when the user logs in. Every message the student types is sent as:

```json
{ "type": "user_message", "message": "explain recursion to me" }
```

Every agent reply comes back as:

```json
{ "type": "agent_message", "agent": "tutor", "text": "Great question! Recursion is..." }
```

---

## API Documentation

Once the backend is running, open:

```
http://localhost:8000/docs
```

Swagger UI with every endpoint, request schema, and response schema.

### Main endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/healthz` | Health check |
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login |
| WS | `/ws/sessions/{id}` | Main chat (WebSocket) |
| GET | `/api/v1/sessions/{id}` | Get session state |
| GET | `/api/v1/profiles/{user_id}` | Get user profile |
| GET | `/api/v1/plans/{user_id}` | Get study plans |
| GET | `/api/v1/rag/query` | Query knowledge base directly |
| GET | `/api/v1/rag/live-examples` | Web search for examples |
| GET | `/metrics` | System metrics |

---

## Project Structure

```
Sir-Project-Tutor-Agent/
├── backend/
│   ├── app/
│   │   ├── main.py                  ← FastAPI app, routes, lifespan
│   │   ├── agents/
│   │   │   ├── base.py              ← BaseAgent + _call_llm() helper
│   │   │   ├── agent_manager.py     ← routes messages, manages session state
│   │   │   ├── orchestrator.py
│   │   │   ├── assessment.py
│   │   │   ├── planning.py
│   │   │   ├── tutor.py
│   │   │   ├── quiz.py
│   │   │   └── feedback.py
│   │   ├── api/routes/
│   │   │   ├── websocket.py         ← /ws/sessions/{id}
│   │   │   ├── auth.py
│   │   │   ├── sessions.py
│   │   │   ├── profiles.py
│   │   │   ├── assessments.py
│   │   │   ├── plans.py
│   │   │   └── rag.py
│   │   ├── core/
│   │   │   ├── config.py            ← reads .env via pydantic-settings
│   │   │   ├── openai_manager.py    ← chat_complete(), web_search(), generate_embedding()
│   │   │   ├── session_store.py     ← MongoDB-backed session storage
│   │   │   └── mongodb.py           ← Beanie init
│   │   ├── guards/
│   │   │   └── schemas.py           ← input/output validation + secret detection
│   │   ├── models/
│   │   ├── services/
│   │   │   ├── rag_service.py       ← coordinates RAG + web search
│   │   │   ├── plan_service.py
│   │   │   └── profile_service.py
│   │   └── tools/
│   │       ├── rag.py               ← Pinecone queries
│   │       └── web_search.py        ← OpenAI web_search_preview
│   ├── tests/
│   ├── .env.example                 ← copy this to .env and fill in keys
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx             ← Landing page
│   │   │   └── dashboard/page.tsx  ← Dashboard
│   │   ├── components/
│   │   │   ├── providers.tsx        ← React Context (user, session, WebSocket)
│   │   │   ├── chat/chat-interface.tsx
│   │   │   ├── dashboard/           ← sidebar, stats, progress, activity
│   │   │   ├── auth/                ← login, register modals
│   │   │   └── landing/
│   │   └── lib/api.ts
│   ├── package.json
│   └── tailwind.config.js
├── docs/                            ← architecture docs
├── SPECIFICATION.md                 ← full technical reference
└── README.md                        ← this file
```

---

## Troubleshooting

### Backend won't start

**"No module named 'openai'"**
```bash
pip install -e .
```

**"MongoDB connection failed"**
- Check your `DATABASE_URL` in `.env` — it must be a full Atlas connection string
- Make sure your IP is whitelisted in Atlas → Network Access

**"pydantic_settings not found"**
```bash
pip install pydantic-settings
```

### Frontend won't start

**"npm: command not found"**  
Install Node.js from nodejs.org

**Build errors about missing packages**
```bash
cd frontend
rm -rf node_modules
npm install
```

### Agents respond with errors

**"Pinecone index unavailable"**  
- Check `PINECONE_API_KEY` in `.env`
- Confirm the index `tutor-lms` exists in your Pinecone console with **dimension 1536**

**"OpenAI API error"**  
- Check `OPENAI_API_KEY` in `.env`
- Make sure your OpenAI account has GPT-4o access (requires billing set up)

**Agent always says "I couldn't find content"**  
Your Pinecone index is empty. Upload course content first (see the Adding Course Content section above).

### WebSocket disconnects immediately

- Make sure the backend is running on port 8000 before opening the frontend
- Check `NEXT_PUBLIC_WS_URL=ws://localhost:8000` is set in `frontend/.env.local`
- Check the browser console for the exact error message

---

## Running Tests

```bash
cd backend
pytest                          # run all tests
pytest --cov=app                # with coverage report
pytest tests/unit/              # unit tests only
pytest tests/integration/       # integration tests only
```

---

## Tech Stack Summary

| What | Technology |
|---|---|
| Backend | FastAPI, Python 3.12, Uvicorn |
| LLM | OpenAI GPT-4o |
| Embeddings | OpenAI text-embedding-3-small (1536 dims) |
| Web Search | OpenAI Responses API — web_search_preview |
| Vector DB | Pinecone (serverless) |
| Database | MongoDB Atlas via Beanie/Motor |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Real-time | WebSocket (FastAPI native) |
| UI libs | Heroicons, Framer Motion, react-hot-toast |

---

For a complete technical reference covering agent internals, session state schema, message protocol, guardrails, and architectural decisions — see **[SPECIFICATION.md](./SPECIFICATION.md)**.
