from pathlib import Path
import json
import requests

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATA_PATH = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"

response = requests.get(DATA_PATH)

data = json.loads(response.text, strict=False)

keywords = set()

for item in data:

    for level in item.get("job_levels", []):
        keywords.add(level.lower().strip())

    for key in item.get("keys", []):
        keywords.add(key.lower().strip())

output_path = BASE_DIR / "data" / "keywords.txt"

with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(keywords)))

print("keywords.txt generated")