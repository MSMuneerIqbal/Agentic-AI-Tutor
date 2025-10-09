# Quickstart Guide: Agent Layer Implementation

## Prerequisites
- Python 3.11+
- uv package manager
- MySQL 8.0+
- Redis 6.0+
- Tavily API key
- OpenAI/Gemini API key

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up virtual environment with uv**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   DATABASE_URL=mysql+pymysql://user:password@localhost:3306/tutor_db
   REDIS_URL=redis://localhost:6379/0
   UV_PACKAGE_MANAGER=uv
   ```

5. **Run database migrations**
   ```bash
   python -m db.migrations
   ```

6. **Start the application**
   ```bash
   uvicorn backend.app.main:app --reload
   ```

## Basic Usage

1. **Start a tutoring session**
   Send a request to the orchestrator to initiate a session:
   ```python
   from models.pydantic_models import AgentRequest
   
   request = AgentRequest(
       agent="assessment",
       session_id="session-uuid",
       trace_id="trace-uuid",
       context={},
       request={"action": "start", "payload": {}}
   )
   ```

2. **Run the assessment flow**
   - The Assessment agent will ask 5 questions
   - Results are saved to MySQL and Redis
   - Planning agent creates a study plan

3. **Engage with the Tutor agent**
   - Tutor will greet the user by name
   - Can operate in TEACH, Q&A, or RE-TEACH modes
   - May fetch live examples via Tavily MCP (continues with generated content if unavailable)

## Testing

1. **Run unit tests**
   ```bash
   pytest tests/unit/
   ```

2. **Run integration tests**
   ```bash
   pytest tests/integration/
   ```

3. **Verify test coverage**
   ```bash
   pytest --cov=backend/ tests/
   ```

## Compliance & Data Retention

- Student data is retained for 1 year after last activity
- Educational compliance (FERPA/COPPA) is enforced
- Accessibility compliance (WCAG 2.1 AA) is maintained
- Security scanning must pass before merge