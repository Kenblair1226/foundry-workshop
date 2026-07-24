"""
Lab 01 - verify_setup.py

Sanity-check that your Azure AI Foundry environment is configured correctly:
  1. .env is present and loaded
  2. The project endpoint is set
  3. DefaultAzureCredential can acquire a token (i.e. `az login` worked)
  4. The Foundry project client can connect and list model deployments

Run from the repo root (with your virtualenv active):
    python labs/01-provision-foundry/verify_setup.py

This script is intentionally defensive: it degrades gracefully and prints
actionable messages instead of raw tracebacks where possible.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def main() -> int:
    # --- 1. Load .env from the repo root ---
    loaded = load_dotenv()
    print(
        "✅ .env loaded" if loaded else "⚠️  No .env file found (using shell env vars)"
    )

    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip()
    if not endpoint or endpoint.startswith("https://<"):
        print(
            "❌ AZURE_AI_PROJECT_ENDPOINT is not set. Edit .env (see Lab 01, step 6)."
        )
        return 1
    print(f"✅ AZURE_AI_PROJECT_ENDPOINT is set: {endpoint}")

    # --- 2. Acquire a Microsoft Entra token via DefaultAzureCredential ---
    try:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        # The Foundry/ML scope; getting a token here proves auth works.
        token = credential.get_token("https://management.azure.com/.default")
        if token and token.token:
            print("✅ DefaultAzureCredential acquired a token")
    except Exception as exc:  # noqa: BLE001 - we want a friendly message
        print(f"❌ DefaultAzureCredential failed: {exc}")
        print("   Fix: run `az login` and `az account set --subscription <id>`.")
        return 1

    # --- 3. Connect to the project and list deployments ---
    try:
        from azure.ai.projects import AIProjectClient

        project = AIProjectClient(endpoint=endpoint, credential=credential)

        print("✅ Connected to project. Deployments found:")
        found_any = False
        # The deployments operations expose the models deployed to this project.
        for dep in project.deployments.list():
            found_any = True
            name = getattr(dep, "name", "<unknown>")
            model = getattr(dep, "model_name", getattr(dep, "model_publisher", ""))
            print(f"   - {name:<24} {model}")
        if not found_any:
            print(
                "   (no deployments yet — deploy gpt-4o in the portal, Lab 01 step 5)"
            )
    except ImportError:
        print(
            "❌ azure-ai-projects not installed. Run: pip install -r requirements.txt"
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  Could not list deployments via the SDK: {exc}")
        print("   This can happen if the deployments API surface differs in your SDK")
        print("   version. Auth still works, so you can proceed to Lab 02.")

    print("🎉 Lab 01 complete — you're ready for Lab 02!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
