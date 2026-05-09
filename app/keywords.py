from pathlib import Path

OFF_TOPIC_KEYWORDS = [
    "salary",
    "legal",
    "law",
    "politics",
    "religion",
    "ignore previous instructions",
    "bypass",
    "hack",
]

BASE_DIR = Path(__file__).resolve().parent.parent

KEYWORDS_PATH = BASE_DIR / "data" / "keywords.txt"

with open(KEYWORDS_PATH, encoding="utf-8") as f:
    IMPORTANT_KEYWORDS = [
        line.strip()
        for line in f.readlines()
    ]