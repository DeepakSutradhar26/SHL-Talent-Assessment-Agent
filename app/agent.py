from app.database import search_catalog
from app.models import ChatResponse

from app.keywords import OFF_TOPIC_KEYWORDS, VAGUE_QUERIES, IMPORTANT_KEYWORDS

# Helper functions
def is_off_topic(query: str) -> bool:
    query = query.lower()

    return any(word in query for word in OFF_TOPIC_KEYWORDS)

def is_vague(query: str) -> bool:

    query = query.lower().strip()

    # Extremely short generic queries
    if query in [
        "assessment",
        "test",
        "need assessment",
        "need a test",
        "hiring",
    ]:
        return True

    # If query contains meaningful hiring context, it is not vague
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in query:
            return False

    # Very short query with no context
    if len(query.split()) <= 2:
        return True

    return False

def get_agent_response(messages):

    latest_message = messages[-1].content

    results = search_catalog(latest_message)

    if not results:
        return ChatResponse(
            reply="No matching assessments found.",
            recommendations=[],
            end_of_conversation=False
        )

    return ChatResponse(
        reply="Here are some recommended assessments based on your query.",
        recommendations=results,
        end_of_conversation=False
    )