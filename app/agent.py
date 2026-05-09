from app.database import search_catalog
from app.models import ChatResponse

from app.keywords import OFF_TOPIC_KEYWORDS, IMPORTANT_KEYWORDS

# Helper functions
def is_off_topic(query: str) -> bool:
    query = query.lower()

    return any(word in query for word in OFF_TOPIC_KEYWORDS)

def is_vague(query: str) -> bool:

    query = query.lower().strip()

    # If query contains meaningful hiring context, it is not vague
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in query:
            return False

    return True

def build_conversation_context(messages):

    user_messages = []

    for msg in messages:
        if msg.role == "user":
            user_messages.append(msg.content)

    return " ".join(user_messages)

def detect_comparison(query: str):

    query = query.lower()

    return (
        "difference between" in query
        or "compare" in query
        or "vs" in query
    )

def get_agent_response(messages):

    latest_message = messages[-1].content

    if is_off_topic(latest_message):

        return ChatResponse(
            reply=(
                "I can only help with SHL assessment "
                "recommendations and comparisons."
            ),
            recommendations=[],
            end_of_conversation=True
        )

    if len(messages) == 1 and is_vague(latest_message):

        return ChatResponse(
            reply=(
                "What role are you hiring for and "
                "what skills or traits do you want to assess?"
            ),
            recommendations=[],
            end_of_conversation=False
        )

    full_query = build_conversation_context(messages)

    if detect_comparison(latest_message):

        results = search_catalog(full_query, n=2)

        if len(results) >= 2:

            a = results[0]
            b = results[1]

            return ChatResponse(
                reply=(
                    f"{a['name']} focuses on "
                    f"{a.get('description', 'specific competencies')}, "
                    f"while {b['name']} focuses on "
                    f"{b.get('description', 'different competencies')}."
                ),
                recommendations=[a, b],
                end_of_conversation=False
            )

    results = search_catalog(full_query, n=10)

    if not results:

        return ChatResponse(
            reply=(
                "I could not find matching SHL assessments "
                "for your request."
            ),
            recommendations=[],
            end_of_conversation=False
        )

    return ChatResponse(
        reply=(
            f"I found {len(results)} SHL assessments "
            "that match your requirements."
        ),
        recommendations=results[:10],
        end_of_conversation=True
    )