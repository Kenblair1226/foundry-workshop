"""
Lab 02 - chat_with_project_client.py

Call a deployed chat model (e.g. GPT-4o) through the Azure AI Foundry project
client. This is the recommended pattern: you authenticate to the *project*
with DefaultAzureCredential (no API keys), and the project hands you an
authenticated inference client for any of its deployments.

Run from the repo root:
    python labs/02-deploy-and-call/chat_with_project_client.py
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

    # Get an azure-ai-inference ChatCompletionsClient scoped to this project.
    # The project injects the correct endpoint + auth automatically.
    chat_client = project.inference.get_chat_completions_client()

    prompt = "Explain what Azure AI Foundry is in one sentence."
    print(f"> Prompt: {prompt}")

    response = chat_client.complete(
        model=deployment,  # the deployment name from Lab 01
        messages=[
            SystemMessage(
                content="You are a concise, accurate cloud solutions architect."
            ),
            UserMessage(content=prompt),
        ],
        temperature=0.3,
        max_tokens=256,
    )

    print(response.choices[0].message.content)

    usage = getattr(response, "usage", None)
    if usage:
        print(
            f"\nTokens — prompt: {usage.prompt_tokens}, "
            f"completion: {usage.completion_tokens}, total: {usage.total_tokens}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
