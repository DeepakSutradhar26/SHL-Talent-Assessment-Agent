import json
import os
import requests

from dotenv import load_dotenv
from app.database import search_catalog
from app.models import ChatResponse, Message
from app.prompts import SYSTEM_PROMPT, CATALOG_CONTEXT_TEMPLATE
from app.query_rewriter import rewrite_query
from typing import List

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"

OFF_TOPIC_KEYWORDS = [
    "salary", "legal", "law", "politics", "religion",
    "ignore previous instructions", "bypass", "hack",
    "forget your instructions", "jailbreak", "pretend you are",
]


def is_off_topic(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in OFF_TOPIC_KEYWORDS)


def is_vague_first_turn(messages: List[Message]) -> bool:
    if len(messages) != 1:
        return False

    words = messages[0].content.lower().split()

    useful_words = {
        "developer", "engineer", "manager", "analyst", "designer",
        "sales", "java", "python", "cognitive", "personality", "aptitude",
        "senior", "junior", "mid", "graduate", "leadership", "technical",
        "numerical", "verbal", "reasoning", "communication",
    }

    has_useful_info = any(w in useful_words for w in words)
    is_short = len(words) < 5

    return is_short and not has_useful_info


def build_catalog_context(query: str) -> str:
    results = search_catalog(query, n=10)

    if not results:
        return "No matching assessments found in the catalog for this query."

    lines = []
    for r in results:
        lines.append(
            f"- Name: {r['name']}\n"
            f"  URL: {r['url']}\n"
            f"  Type: {'Personality (P)' if r['test_type'] == 'P' else 'Knowledge/Skills (K)'}\n"
            f"  Details: {r['description'][:300]}"
        )

    return CATALOG_CONTEXT_TEMPLATE.format(catalog_items="\n".join(lines))


def call_llm(messages: List[dict], system: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": 1024,
        "messages": [{"role": "system", "content": system}] + messages,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=body,
        timeout=25,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def validate_recommendations(raw_recs: list, query: str) -> list:
    valid = []
    for rec in raw_recs:
        url = rec.get("url", "")
        name = rec.get("name", "")
        test_type = rec.get("test_type", "K")

        if not url.startswith("https://www.shl.com"):
            continue

        if test_type not in ("K", "P"):
            test_type = "K"

        valid.append({
            "name": name,
            "url": url,
            "test_type": test_type,
        })

    return valid[:10]


def get_agent_response(messages: List[Message]) -> ChatResponse:
    latest_message = messages[-1].content

    if is_off_topic(latest_message):
        return ChatResponse(
            reply="I can only help with SHL assessment selection. Please ask me about finding the right assessments for a role.",
            recommendations=[],
            end_of_conversation=True,
        )

    if is_vague_first_turn(messages):
        return ChatResponse(
            reply="Happy to help find the right SHL assessments! Could you tell me a bit more about the role you're hiring for, and what skills you want to assess — for example, technical ability, cognitive reasoning, or personality?",
            recommendations=[],
            end_of_conversation=False,
        )

    search_query = rewrite_query(messages)

    catalog_context = build_catalog_context(search_query)

    llm_messages = []
    for i, msg in enumerate(messages):
        if i == len(messages) - 1:
            # Last message gets the catalog context appended
            content = f"{msg.content}\n\n{catalog_context}"
        else:
            content = msg.content
        llm_messages.append({"role": msg.role, "content": content})

    try:
        raw_response = call_llm(llm_messages, SYSTEM_PROMPT)
    except Exception as e:
        print(f"Claude API error: {e}")
        return ChatResponse(
            reply="I'm having trouble connecting right now. Please try again in a moment.",
            recommendations=[],
            end_of_conversation=False,
        )

    try:
        clean = raw_response.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1]
            if clean.startswith("json"):
                clean = clean[4:]
        parsed = json.loads(clean.strip())
    except json.JSONDecodeError:
        return ChatResponse(
            reply="I found some relevant assessments but had trouble formatting the response. Please try rephrasing your question.",
            recommendations=[],
            end_of_conversation=False,
        )

    raw_recs = parsed.get("recommendations", [])
    safe_recs = validate_recommendations(raw_recs, search_query)

    return ChatResponse(
        reply=parsed.get("reply", "Here are my recommendations."),
        recommendations=safe_recs,
        end_of_conversation=parsed.get("end_of_conversation", False),
    )