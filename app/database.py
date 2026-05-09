import chromadb
import os

from dotenv import load_dotenv

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')

client = chromadb.PersistentClient(path="./chroma_db")

embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    token=HF_TOKEN
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