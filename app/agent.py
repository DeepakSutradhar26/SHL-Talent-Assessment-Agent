from app.database import search_catalog
from app.models import ChatResponse
from app.keywords import OFF_TOPIC_KEYWORDS, IMPORTANT_KEYWORDS


def normalize(text: str) -> str:
    return text.lower().strip()


def is_off_topic(query: str) -> bool:
    query = normalize(query)
    return any(word in query for word in OFF_TOPIC_KEYWORDS)


def is_vague(query: str) -> bool:
    query = normalize(query)

    weak_patterns = [
        "need assessment",
        "need a test",
        "assessment",
        "test",
        "hiring",
        "looking for assessment"
    ]

    if any(p in query for p in weak_patterns):
        return True

    # if query already contains strong intent
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in query:
            return False

    return True


def build_conversation_context(messages):
    return " ".join(
        msg.content for msg in messages if msg.role == "user"
    )


def detect_comparison(query: str) -> bool:
    query = normalize(query)

    return any([
        "difference between" in query,
        "compare" in query,
        "vs" in query,
        "versus" in query
    ])


def detect_refinement(query: str) -> bool:
    query = normalize(query)

    return any([
        "add" in query,
        "include" in query,
        "also" in query,
        "instead" in query,
        "change" in query
    ])


def get_agent_response(messages):

    latest_message = messages[-1].content

    # 1. OFF-TOPIC HANDLING
    if is_off_topic(latest_message):
        return ChatResponse(
            reply="I can only help with SHL assessment recommendations and comparisons.",
            recommendations=[],
            end_of_conversation=True
        )

    # 2. CONTEXT BUILD
    full_query = build_conversation_context(messages)

    # 3. COMPARISON INTENT
    if detect_comparison(latest_message):

        results = search_catalog(full_query, n=2)
       
        a, b = results[0], results[1]

        return ChatResponse(
            reply=f"{a['name']} and {b['name']} are different SHL assessments serving different evaluation purposes.",
            recommendations=[a, b],
            end_of_conversation=False
        )

    # 4. REFINEMENT
    if detect_refinement(latest_message) and len(messages) > 1:

        results = search_catalog(full_query, n=10)

        return ChatResponse(
            reply=f"I've updated your shortlist based on the new requirements. Here are the refined assessments.",
            recommendations=results,
            end_of_conversation=False
        )

    # 5. VAGUE FIRST TURN
    if len(messages) == 1 and is_vague(latest_message):

        return ChatResponse(
            reply=(
                "Could you clarify the role you're hiring for and "
                "the key skills you want to assess (e.g. technical, personality, leadership)?"
            ),
            recommendations=[],
            end_of_conversation=False
        )

    # 6. NORMAL RETRIEVAL
    results = search_catalog(full_query, n=10)

    if not results:
        return ChatResponse(
            reply="I couldn't find matching SHL assessments for your request.",
            recommendations=[],
            end_of_conversation=False
        )

    return ChatResponse(
        reply=f"I found {len(results)} SHL assessments that match your requirements.",
        recommendations=results,
        end_of_conversation=True
    )