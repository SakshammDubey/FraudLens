
from pathlib import Path

import chromadb

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "fraudlens_knowledge"


def retrieve_context(question: str, top_k: int = 4) -> list[dict]:
    if not question.strip():
        return []

    client = chromadb.PersistentClient(path=str(DB_DIR))

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=(
                chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
            ),
        )
    except Exception as exc:
        raise RuntimeError(
            "Knowledge base not found. Run: python -m rag.ingest"
        ) from exc

    count = collection.count()

    if count == 0:
        return []

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, count),
        include=["documents", "metadatas", "distances"],
    )

    evidence = []

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        evidence.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "chunk": metadata.get("chunk", -1),
            "distance": distance,
        })

    return evidence


if __name__ == "__main__":
    question = input("Ask about fraud investigation: ")

    for item in retrieve_context(question):
        print(f"\nSource: {item['source']}")
        print(f"Chunk: {item['chunk']}")
        print(item["text"])
