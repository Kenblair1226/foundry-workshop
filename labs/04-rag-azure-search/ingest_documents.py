"""
Lab 04 - ingest_documents.py

Bring-your-own-data ingestion for RAG:
  1. Read local documents from ./data
  2. Split them into overlapping text chunks
  3. Embed each chunk with an Azure AI Foundry embedding deployment
     (text-embedding-3-large) via the azure-ai-inference EmbeddingsClient
  4. Create (or update) an Azure AI Search index with a vector field
  5. Upload the chunks + embeddings as searchable documents

Run from the repo root:
    python labs/04-rag-azure-search/ingest_documents.py

Required .env values:
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, AZURE_SEARCH_INDEX_NAME
    AZURE_AI_PROJECT_ENDPOINT  (keyless embeddings via the project client)
    EMBEDDING_MODEL_DEPLOYMENT (e.g. text-embedding-3-large)

Auth notes:
  - Embeddings use the Foundry *project* client with DefaultAzureCredential
    (keyless). To use a direct inference endpoint + key instead, see the
    commented alternative in `get_embeddings_client()`.
  - Azure AI Search uses an admin API key here for classroom simplicity. In
    production prefer a managed identity + the `Search Index Data Contributor`
    role and `DefaultAzureCredential`.
"""

from __future__ import annotations

import glob
import os
import sys
from typing import List

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SearchableField,
    SimpleField,
    SearchIndex,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)

# text-embedding-3-large returns 3072-dimensional vectors by default.
EMBEDDING_DIMENSIONS = 3072
CHUNK_SIZE = 800  # characters
CHUNK_OVERLAP = 150  # characters
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def chunk_text(
    text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """Naive fixed-size character chunker with overlap.

    Real pipelines usually split on semantic boundaries (headings, sentences,
    tokens). Character chunking keeps this lab dependency-free and easy to read.
    """
    text = text.strip()
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start = end - overlap  # step back to create overlap
    return [c for c in chunks if c]


def load_documents() -> List[dict]:
    """Load .md/.txt files from ./data and return chunk records."""
    records: List[dict] = []
    paths = sorted(
        glob.glob(os.path.join(DATA_DIR, "*.md"))
        + glob.glob(os.path.join(DATA_DIR, "*.txt"))
    )
    if not paths:
        print(f"❌ No .md/.txt files found in {DATA_DIR}")
        return records

    for path in paths:
        source = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        for i, chunk in enumerate(chunk_text(content)):
            records.append(
                {
                    # Search keys must be safe for the URL-ish key charset.
                    "id": f"{source}-{i}".replace(".", "_").replace(" ", "_"),
                    "content": chunk,
                    "source": source,
                }
            )
    print(f"Loaded {len(records)} chunks from {len(paths)} file(s).")
    return records


def get_embeddings_client():
    """Return an azure-ai-inference EmbeddingsClient via the Foundry project."""
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip()
    if not endpoint or endpoint.startswith("https://<"):
        raise SystemExit("❌ Set AZURE_AI_PROJECT_ENDPOINT in .env (see Lab 01).")

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())
    return project.inference.get_embeddings_client()

    # --- Alternative: direct inference endpoint + API key ---
    # from azure.ai.inference import EmbeddingsClient
    # from azure.core.credentials import AzureKeyCredential
    # return EmbeddingsClient(
    #     endpoint=os.getenv("AZURE_INFERENCE_ENDPOINT"),
    #     credential=AzureKeyCredential(os.getenv("AZURE_INFERENCE_API_KEY")),
    # )


def embed_chunks(records: List[dict], deployment: str) -> None:
    """Embed each chunk and attach a `content_vector` field in place."""
    client = get_embeddings_client()
    texts = [r["content"] for r in records]

    # The Embeddings API accepts a batch of inputs in a single call.
    result = client.embed(model=deployment, input=texts)
    for record, item in zip(records, result.data):
        record["content_vector"] = item.embedding
    print(f"Embedded {len(records)} chunks with deployment '{deployment}'.")


def ensure_index(index_client: SearchIndexClient, index_name: str) -> None:
    """Create the index (idempotent) with a vector search profile."""
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(
            name="source",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="hnsw-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-config")],
        profiles=[
            VectorSearchProfile(
                name="hnsw-profile", algorithm_configuration_name="hnsw-config"
            )
        ],
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)
    print(f"Index '{index_name}' is ready.")


def main() -> int:
    load_dotenv()

    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").strip()
    search_key = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "workshop-rag-index").strip()
    deployment = os.getenv(
        "EMBEDDING_MODEL_DEPLOYMENT", "text-embedding-3-large"
    ).strip()

    if not search_endpoint or search_endpoint.startswith("https://<") or not search_key:
        print("❌ Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY in .env.")
        return 1

    records = load_documents()
    if not records:
        return 1

    embed_chunks(records, deployment)

    credential = AzureKeyCredential(search_key)
    index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)
    ensure_index(index_client, index_name)

    search_client = SearchClient(
        endpoint=search_endpoint, index_name=index_name, credential=credential
    )
    result = search_client.upload_documents(documents=records)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(records)} documents to '{index_name}'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
