from fastapi import FastAPI
from app.models import ChatRequest, ChatResponse
from app.agent import get_agent_response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/health")
def health():
    """Required health check for the assignment."""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint."""
    return get_agent_response(request.messages)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)