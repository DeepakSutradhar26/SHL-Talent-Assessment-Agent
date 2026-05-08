from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


def is_vague_query(text: str) -> bool:

    vague_phrases = [
        "need assessment",
        "need a test",
        "hiring",
        "assessment",
        "looking for test"
    ]

    text = text.lower()

    return any(phrase in text for phrase in vague_phrases)


def detect_role(text: str):

    roles = [
        "java developer",
        "python developer",
        "data scientist",
        "sales manager",
        "backend developer"
    ]

    text = text.lower()

    for role in roles:
        if role in text:
            return role

    return None


@router.post("/chat")
def chat(req: ChatRequest):

    latest_message = req.messages[-1].content

    role = detect_role(latest_message)

    if is_vague_query(latest_message) and not role:

        return {
            "reply": "Sure. What role are you hiring for and what seniority level?",
            "recommendations": [],
            "end_of_conversation": False
        }

    if role:

        recommendations = [
            {
                "name": "Java 8 (New)",
                "url": "https://www.shl.com",
                "test_type": "K"
            }
        ]

        return {
            "reply": f"I found assessments for a {role}.",
            "recommendations": recommendations,
            "end_of_conversation": True
        }

    return {
        "reply": "Could you provide more hiring requirements?",
        "recommendations": [],
        "end_of_conversation": False
    }