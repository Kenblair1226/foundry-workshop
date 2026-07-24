"""
Lab 02 - chat_streaming.py

Stream a chat completion token-by-token from a deployed model using the
Azure AI Foundry project client. Streaming improves perceived latency for
chat UIs.

Run from the repo root:
    python labs/02-deploy-and-call/chat_streaming.py
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import SystemMessage, UserMessage


def main() -> int:
    load_dotenv()

    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip()
    deployment = os.getenv("CHAT_MODEL_DEPLOYMENT", "gpt-4o").strip()
    if not endpoint or endpoint.startswith("https://<"):
        print("❌ Set AZURE_AI_PROJECT_ENDPOINT in .env (see Lab 01).")
        return 1

    credential = DefaultAzureCredential()
    project = AIProjectClient(endpoint=endpoint, credential=credential)
    chat_client = project.inference.get_chat_completions_client()

    print("> Streaming answer:\n")
    stream = chat_client.complete(
        model=deployment,
        messages=[
            SystemMessage(content="You are a helpful teaching assistant."),
            UserMessage(
                content="List 3 benefits of retrieval-augmented generation (RAG). Keep it brief."
            ),
        ],
        temperature=0.5,
        max_tokens=300,
        stream=True,
    )

    for update in stream:
        # Each update is a partial chunk; guard against empty choices/deltas.
        if update.choices:
            delta = update.choices[0].delta
            if delta and delta.content:
                print(delta.content, end="", flush=True)

    print("\n\n[✓ stream complete]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
