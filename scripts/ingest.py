import requests
import chromadb
import pandas as pd
import json
import os

from dotenv import load_dotenv
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()

# Config
DATA_PATH = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"
DB_PATH = "./chroma_db"
HF_TOKEN = os.getenv("HF_TOKEN")

def run_ingestion():
    # Download Catalog
    print("Step1: Downloading catalog...")
    try:
        res = requests.get(DATA_PATH)
        res.raise_for_status()
        raw_data = json.loads(res.text, strict=False)
    except Exception as e:
        print(f"Error downloading data: {e}")
        return
    
    # Cleaning and Transformation
    print("Step2: Cleaning and Transforming data")
    df = pd.DataFrame(raw_data)
    df = df.replace(r'^\s*$', pd.NA, regex=True)
    df = df.drop_duplicates(subset=["entity_id"])

    # Initialize Vector DB
    client = chromadb.PersistentClient(path=DB_PATH)

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.get_or_create_collection(
        name="shl_assessments",
        embedding_function=embedding_function
    )

    docs, metas, ids = [], [], []

    # Process the catalog
    for _,row in df.iterrows():
        job_levels = ", ".join(row["job_levels"]) if isinstance(row["job_levels"], list) else str(row["job_levels"])
        keys = ", ".join(row["keys"]) if isinstance(row["keys"], list) else str(row["keys"])

        search_text = (
            f"Assessment: {row['name']}. "
            f"Description: {row['description']}. "
            f"Target Levels: {job_levels}. "
            f"Categories: {keys}."
        )

        docs.append(search_text)
        metas.append({
            "name": str(row['name']),
            "url": str(row['link']),
            "test_type": "P" if "Personality" in keys else "K"
        })
        ids.append(str(row['entity_id']))

    # Save to database
    print(f"Step 3: Indexing {len(docs)} items into ChromaDB...")
    collection.add(documents=docs, metadatas=metas, ids=ids)
    print("Success! Database built and ready for the Agent.")

if __name__ == "__main__":
    run_ingestion()