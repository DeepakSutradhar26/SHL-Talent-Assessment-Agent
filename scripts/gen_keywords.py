import requests
import json
from pathlib import Path

CATALOG_URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

print("Downloading catalog to extract keywords...")
response = requests.get(CATALOG_URL, timeout=30)
data = json.loads(response.text, strict=False)

keywords = set()

for item in data:
    for level in item.get("job_levels", []):
        keywords.add(level.lower().strip())
    for key in item.get("keys", []):
        keywords.add(key.lower().strip())

output_path = DATA_DIR / "keywords.txt"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(keywords)))

print(f"Done! Saved {len(keywords)} keywords to {output_path}")