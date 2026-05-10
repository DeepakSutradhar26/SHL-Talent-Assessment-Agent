import requests
import chromadb
import pandas as pd
import json
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()

CATALOG_URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"
DB_PATH = "./chroma_db"


def run_ingestion():
    print("Step 1: Downloading SHL catalog...")
    try:
        response = requests.get(CATALOG_URL, timeout=30)
        response.raise_for_status()
        raw_data = json.loads(response.text, strict=False)
        print(f"  Downloaded {len(raw_data)} items.")
    except Exception as e:
        print(f"Error downloading catalog: {e}")
        return

    print("Step 2: Cleaning data...")
    df = pd.DataFrame(raw_data)
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.drop_duplicates(subset=["entity_id"])
    print(f"  {len(df)} unique assessments after cleaning.")

    print("Step 3: Setting up vector database...")
    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_or_create_collection(
        name="shl_assessments",
        embedding_function=embedding_function,
    )

    docs, metas, ids = [], [], []

    for _, row in df.iterrows():
        job_levels = ", ".join(row["job_levels"]) if isinstance(row["job_levels"], list) else str(row.get("job_levels", ""))
        keys = ", ".join(row["keys"]) if isinstance(row["keys"], list) else str(row.get("keys", ""))

        search_text = (
            f"Assessment: {row['name']}. "
            f"Description: {row['description']}. "
            f"Target Levels: {job_levels}. "
            f"Categories: {keys}."
        )

        docs.append(search_text)
        metas.append({
            "name": str(row["name"]),
            "url": str(row["link"]),
            "test_type": "P" if "Personality" in keys else "K",
        })
        ids.append(str(row["entity_id"]))

    print(f"Step 4: Indexing {len(docs)} assessments into ChromaDB...")
    batch_size = 100
    for i in range(0, len(docs), batch_size):
        collection.add(
            documents=docs[i:i+batch_size],
            metadatas=metas[i:i+batch_size],
            ids=ids[i:i+batch_size],
        )
    print(f"Done! Database is ready at {DB_PATH}/")


if __name__ == "__main__":
    run_ingestion()