"""
Project: Customer 360 Analytics Platform
Author: Mahinul Mannan
Role: Data Scientist / Machine Learning Engineer
Description: Index retention policy documents into Qdrant for RAG retrieval.
"""
import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Configuration
POLICY_FILE_PATH = "data/policies/retention_policy.txt"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "retention_policies"
EMBEDDING_MODEL = "BAAI/bge-m3"
CHUNK_SIZE = 512
OVERLAP = 50

def chunk_text(text: str) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), CHUNK_SIZE - OVERLAP):
        chunk = " ".join(words[i:i + CHUNK_SIZE])
        if chunk:
            chunks.append(chunk)
    return chunks

def main():
    print("🚀 Starting RAG Indexing...")
    
    # 1. Load embedding model
    print("📥 Loading embedding model...")
    encoder = SentenceTransformer(EMBEDDING_MODEL)
    
    # 2. Connect to Qdrant
    print("🔌 Connecting to Qdrant...")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 3. Read the policy file
    if not os.path.exists(POLICY_FILE_PATH):
        print(f"❌ File not found: {POLICY_FILE_PATH}")
        return
    
    with open(POLICY_FILE_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    
    # 4. Chunk the text
    chunks = chunk_text(text)
    print(f"📄 Created {len(chunks)} chunks.")
    
    # 5. Create collection if not exists
    collections = client.get_collections().collections
    if COLLECTION_NAME not in [c.name for c in collections]:
        print(f"🆕 Creating collection: {COLLECTION_NAME}")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1024,  # Dimension for bge-m3
                distance=models.Distance.COSINE
            )
        )
    
    # 6. Generate embeddings and upload
    print("🧠 Generating embeddings and uploading...")
    points = []
    for idx, chunk in enumerate(chunks):
        embedding = encoder.encode(chunk).tolist()
        points.append(
            models.PointStruct(
                id=uuid.uuid4().int % 10**9,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": "retention_policy.txt",
                    "chunk_index": idx
                }
            )
        )
    
    # 7. Upsert points
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"✅ Successfully indexed {len(points)} chunks into Qdrant.")
    print("🎉 Indexing complete!")

if __name__ == "__main__":
    main()