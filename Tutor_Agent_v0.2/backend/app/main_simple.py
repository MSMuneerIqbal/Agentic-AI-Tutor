"""Simple FastAPI application without complex dependencies."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Tutor GPT API",
    description="AI-Powered Learning Platform",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Tutor GPT API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint."""
    return {
        "message": "Backend is working!",
        "status": "success"
    }

@app.get("/api/v1/agents")
async def get_agents():
    """Get available agents."""
    return {
        "agents": [
            {"name": "Tutor", "status": "ready"},
            {"name": "Planning", "status": "ready"},
            {"name": "Assessment", "status": "ready"},
            {"name": "Quiz", "status": "ready"},
            {"name": "Orchestrator", "status": "ready"},
            {"name": "Feedback", "status": "ready"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
