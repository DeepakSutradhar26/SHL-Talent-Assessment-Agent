import chromadb

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

client = chromadb.PersistentClient(path="./chroma_db")

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="shl_assessments",
    embedding_function=embedding_function
)

def search_catalog(query: str, n=5):

    if not query:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n
    )

    return results["metadatas"][0]