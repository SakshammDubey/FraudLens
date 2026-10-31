
from pathlib import Path
import hashlib

import chromadb
from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "documents"
DB_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "fraudlens_knowledge"
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150


def read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

    return path.read_text(encoding="utf-8", errors="ignore")


def split_text(text: str) -> list[str]:
    text = " ".join(text.split())
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def main():
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(DB_DIR))

    embedding_function = (
        chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0

    for path in sorted(DOCUMENTS_DIR.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".txt", ".md", ".pdf"}:
            continue

        text = read_document(path)
        chunks = split_text(text)

        if not chunks:
            print(f"Skipped empty document: {path.name}")
            continue

        ids = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            chunk_id = hashlib.sha256(
                f"{path.resolve()}:{index}:{chunk}".encode("utf-8")
            ).hexdigest()

            ids.append(chunk_id)
            metadatas.append({
                "source": path.name,
                "chunk": index,
            })

        collection.upsert(
            ids=ids,
            documents=chunks,
            metadatas=metadatas,
        )

        total_chunks += len(chunks)
        print(f"Indexed {path.name}: {len(chunks)} chunks")

    print(f"Knowledge base ready. Processed {total_chunks} chunks.")
    print(f"Stored in: {DB_DIR}")


if __name__ == "__main__":
    main()
