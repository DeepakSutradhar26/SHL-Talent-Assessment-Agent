from typing import List

ROLE_EXPANSIONS = {
    "software":    ["technical", "coding", "programming"],
    "developer":   ["technical", "coding", "programming"],
    "engineer":    ["technical", "analytical", "problem solving"],
    "java":        ["java", "backend", "technical", "programming"],
    "python":      ["python", "technical", "scripting"],
    "data":        ["analytical", "numerical", "reasoning"],
    "manager":     ["leadership", "management", "communication"],
    "sales":       ["communication", "persuasion", "interpersonal"],
    "analyst":     ["analytical", "reasoning", "numerical"],
    "hr":          ["interpersonal", "communication", "personality"],
    "finance":     ["numerical", "analytical", "attention to detail"],
    "customer":    ["communication", "interpersonal", "service"],
    "marketing":   ["creativity", "communication", "verbal"],
    "senior":      ["experienced", "leadership", "strategic"],
    "junior":      ["graduate", "entry level", "aptitude"],
    "graduate":    ["entry level", "aptitude", "potential"],
    "lead":        ["leadership", "management", "mentoring"],
    "executive":   ["leadership", "strategic", "decision making"],
    "personality": ["personality", "behavioural", "OPQ"],
    "cognitive":   ["cognitive", "reasoning", "aptitude", "numerical", "verbal"],
    "leadership":  ["leadership", "management", "decision making"],
    "numerical":   ["numerical", "mathematical", "quantitative"],
    "verbal":      ["verbal", "reading", "comprehension"],
}


def rewrite_query(messages: List) -> str:
    if not messages:
        return ""

    user_turns = [m.content.strip() for m in messages if m.role == "user"]

    if not user_turns:
        return ""

    base = " ".join(user_turns)

    # Extra weightage to last chat
    last_turn_boost = user_turns[-1] if len(user_turns) > 1 else ""

    combined = f"{base} {last_turn_boost}".lower()

    seen = set()
    expansions = []

    for keyword, related_terms in ROLE_EXPANSIONS.items():
        if keyword in combined:
            for term in related_terms:
                if term not in seen and term not in combined:
                    expansions.append(term)
                    seen.add(term)

    if expansions:
        combined = combined + " " + " ".join(expansions)

    return combined.strip()