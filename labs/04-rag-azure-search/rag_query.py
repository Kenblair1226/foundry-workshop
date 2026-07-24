"""
Lab 04 - rag_query.py

Retrieval-Augmented Generation query pipeline:
  1. Embed the user's question (same embedding deployment used for ingestion)
  2. Run a vector search against the Azure AI Search index to retrieve the
     top-k most relevant chunks
  3. "Stuff" those chunks into the system prompt as grounding context
  4. Call the chat deployment and print a grounded, cited answer

Run from the repo root (after ingest_documents.py):
    python labs/04-rag-azure-search/rag_query.py "What is the Enterprise SLA?"

Required .env values:
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_API_KEY, AZURE_SEARCH_INDEX_NAME
    AZURE_AI_PROJECT_ENDPOINT
    EMBEDDING_MODEL_DEPLOYMENT, CHAT_MODEL_DEPLOYMENT
"""

from __future__ import annotations

import os
import sys
from typing import List

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

TOP_K = 3


def embed_query(project: AIProjectClient, deployment: str, text: str) -> List[float]:
    embeddings = project.inference.get_embeddings_client()
    result = embeddings.embed(model=deployment, input=[text])
    return result.data[0].embedding


def retrieve(search_client: SearchClient, query_vector: List[float]) -> List[dict]:
    """Vector search for the top-k relevant chunks."""
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=TOP_K,
        fields="content_vector",
    )
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["id", "content", "source"],
    )
    return list(results)


def build_context(chunks: List[dict]) -> str:
    """Format retrieved chunks into a numbered, citable context block."""
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"[{i}] (source: {chunk['source']})\n{chunk['content']}")
    return "\n\n".join(lines)


def main() -> int:
    load_dotenv()

    question = " ".join(sys.argv[1:]).strip() or "What is the Enterprise SLA?"

    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip()
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "").strip()
    search_key = os.getenv("AZURE_SEARCH_API_KEY", "").strip()
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "workshop-rag-index").strip()
    embed_deployment = os.getenv(
        "EMBEDDING_MODEL_DEPLOYMENT", "text-embedding-3-large"
    ).strip()
    chat_deployment = os.getenv("CHAT_MODEL_DEPLOYMENT", "gpt-4o").strip()

    if not project_endpoint or project_endpoint.startswith("https://<"):
        print("❌ Set AZURE_AI_PROJECT_ENDPOINT in .env (see Lab 01).")
        return 1
    if not search_endpoint or search_endpoint.startswith("https://<") or not search_key:
        print("❌ Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_API_KEY in .env.")
        return 1

    project = AIProjectClient(
        endpoint=project_endpoint, credential=DefaultAzureCredential()
    )
    search_client = SearchClient(
        endpoint=search_endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(search_key),
    )

    print(f"> Question: {question}\n")

    query_vector = embed_query(project, embed_deployment, question)
    chunks = retrieve(search_client, query_vector)
    if not chunks:
        print("No results retrieved — did you run ingest_documents.py first?")
        return 1

    context = build_context(chunks)
    print("Retrieved context:")
    for i, chunk in enumerate(chunks, start=1):
        preview = chunk["content"][:80].replace("\n", " ")
        print(f"  [{i}] {chunk['source']}: {preview}...")
    print()

    system_prompt = (
        "You are a helpful assistant for the Contoso Cloud AI Platform. "
        "Answer the user's question using ONLY the numbered context passages "
        "below. If the answer is not in the context, say you don't know. "
        "Cite the passages you used with their bracket numbers, e.g. [1].\n\n"
        f"Context:\n{context}"
    )

    chat_client = project.inference.get_chat_completions_client()
    response = chat_client.complete(
        model=chat_deployment,
        messages=[
            SystemMessage(content=system_prompt),
            UserMessage(content=question),
        ],
        temperature=0.2,
        max_tokens=400,
    )

    print("=== Grounded answer ===")
    print(response.choices[0].message.content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
