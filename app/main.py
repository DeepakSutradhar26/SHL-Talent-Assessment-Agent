from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse
from app.agent import get_agent_response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SHL Assessment Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return get_agent_response(request.messages)