import chromadb
import os

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

DB_PATH = "./chroma_db"

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="shl_assessments",
    embedding_function=embedding_function,
)


def search_catalog(query: str, n: int = 10) -> list:
    total = collection.count()
    if total == 0:
        return []

    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(30, total),
        )
    except Exception as e:
        print(f"Search error: {e}")
        return []

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    scored = []
    for doc, meta, dist in zip(docs, metas, distances):
        score = 1 - dist

        name = meta.get("name", "").lower()
        test_type = meta.get("test_type", "K")

        if test_type in ("K", "P"):
            score += 0.03

        for word in query.lower().split():
            if len(word) > 3 and word in name:
                score += 0.08

        scored.append({
            "name": meta.get("name", ""),
            "url": meta.get("url", ""),
            "test_type": test_type,
            "description": doc,
            "score": score,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored[:n]