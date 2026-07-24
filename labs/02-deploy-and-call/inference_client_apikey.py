"""
Lab 02 - inference_client_apikey.py

Call a deployed model using the azure-ai-inference SDK directly with an API key
(AzureKeyCredential). Use this pattern when you want a self-contained script
that only needs an endpoint + key (e.g. in a classroom or CI setting) and don't
want to depend on interactive `az login`.

Prefer DefaultAzureCredential (keyless) for production. See
chat_with_project_client.py for the keyless approach.

Run from the repo root:
    python labs/02-deploy-and-call/inference_client_apikey.py
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage


def main() -> int:
    load_dotenv()

    endpoint = os.getenv("AZURE_INFERENCE_ENDPOINT", "").strip()
    api_key = os.getenv("AZURE_INFERENCE_API_KEY", "").strip()
    deployment = os.getenv("CHAT_MODEL_DEPLOYMENT", "gpt-4o").strip()

    if not endpoint or endpoint.startswith("https://<") or not api_key:
        print("❌ Set AZURE_INFERENCE_ENDPOINT and AZURE_INFERENCE_API_KEY in .env.")
        print(
            "   Find them under Project > Models + endpoints > <deployment> > Endpoint."
        )
        return 1

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
        # api_version is optional; the SDK ships a sensible default.
    )

    # A short multi-turn conversation demonstrating message roles.
    messages = [
        SystemMessage(content="You are a witty but accurate Azure expert."),
        UserMessage(
            content="What's the difference between a Foundry hub and a project?"
        ),
        AssistantMessage(
            content="A hub is the shared, team-level resource; a project is a "
            "workspace inside it where you build a specific app."
        ),
        UserMessage(content="Great — now give me a one-line analogy."),
    ]

    response = client.complete(
        model=deployment,
        messages=messages,
        temperature=0.7,
        max_tokens=120,
    )

    print("Assistant:", response.choices[0].message.content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
