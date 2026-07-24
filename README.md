# Building AI Applications with Azure AI Foundry — Hands-on Workshop

A complete, self-contained, one-day workshop that takes you from zero to a
deployed AI agent on **Microsoft Azure AI Foundry** (the unified platform
formerly known as Azure AI Studio). It combines a presentation deck with five
progressive, runnable hands-on labs.

> **What is Azure AI Foundry?** A unified platform for designing, customizing,
> evaluating, and managing generative-AI applications and agents at scale. It
> brings together a model catalog (Azure OpenAI, Microsoft, Meta, Mistral,
> Hugging Face, and more), a project-based workspace, prompt flow, evaluation,
> RAG tooling, and the Agent Service — all accessible from the
> [Foundry portal](https://ai.azure.com) and the Foundry SDKs.

---

## Repository structure

```
foundry-workshop/
├── README.md                 # You are here
├── AGENDA.md                 # Detailed timed agenda
├── LICENSE                   # MIT
├── requirements.txt          # Shared Python dependencies for all labs
├── .env.example              # Template for endpoints/keys (copy to .env)
├── .gitignore
├── labs/
│   ├── 01-provision-foundry/ # Provision a hub + project, explore the portal
│   ├── 02-deploy-and-call/   # Deploy GPT-4o & call it from Python
│   ├── 03-prompt-and-eval/   # Prompt engineering + evaluation
│   ├── 04-rag-azure-search/  # RAG with Azure AI Search
│   └── 05-agent-service/     # Build & deploy an Agent
└── slides/
    ├── foundry-workshop.md   # Marp slide deck (Markdown)
    └── README.md             # How to render the deck
```

---

## Prerequisites

Before the workshop, make sure you have:

| Requirement                | Details                                                                                                   |
| -------------------------- | --------------------------------------------------------------------------------------------------------- |
| **Azure subscription**     | With permission to create resources. A pay-as-you-go or sponsored subscription works. [Free account](https://azure.microsoft.com/free/). |
| **Azure AI Foundry access**| Access to [ai.azure.com](https://ai.azure.com). Your account needs `Owner` or `Contributor` + `Azure AI Developer` role on the resource group. |
| **Azure OpenAI quota**     | Quota for at least one GPT-4o (or GPT-4o-mini) deployment in a supported region (e.g. `eastus2`, `swedencentral`). |
| **Python 3.11+**           | `python --version` should report 3.11 or newer.                                                           |
| **Azure CLI**              | `az --version` ≥ 2.60. [Install guide](https://learn.microsoft.com/cli/azure/install-azure-cli).          |
| **Git**                    | To clone this repo.                                                                                        |
| **VS Code (recommended)**  | With the Python and *Azure AI Foundry* extensions.                                                         |

### One-time setup

```bash
# 1. Clone the repo
git clone <this-repo-url> foundry-workshop
cd foundry-workshop

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install shared dependencies
pip install -r requirements.txt

# 4. Sign in to Azure (used by DefaultAzureCredential)
az login
az account set --subscription "<your-subscription-id>"

# 5. Copy the environment template and fill it in as you go
cp .env.example .env
```

> 🔐 **Security note:** All labs read configuration from `.env` (via
> `python-dotenv`) or from `DefaultAzureCredential`. **Never** hardcode keys or
> commit your `.env` file — it is already listed in `.gitignore`. Prefer
> Microsoft Entra ID (keyless) auth wherever possible.

---

## Authentication model

The labs favour **keyless authentication** using `DefaultAzureCredential` from
`azure-identity`. This credential automatically tries, in order: environment
variables, managed identity, the Azure CLI (`az login`), VS Code, and more.
This means you generally do **not** need API keys for the Foundry project
client — signing in with `az login` is enough.

API-key auth is shown as an alternative for the `azure-ai-inference` and Azure
AI Search samples, where it can be convenient in a classroom setting.

---

## The labs

| #  | Lab                                                             | You will…                                                             | Time   |
| -- | -------------------------------------------------------------- | --------------------------------------------------------------------- | ------ |
| 01 | [Provision Foundry](./labs/01-provision-foundry/README.md)     | Create a hub + project, explore the portal, deploy your first model   | 45 min |
| 02 | [Deploy & Call a Model](./labs/02-deploy-and-call/README.md)   | Call GPT-4o with `azure-ai-projects` and `azure-ai-inference`         | 60 min |
| 03 | [Prompt & Evaluate](./labs/03-prompt-and-eval/README.md)       | Engineer prompts and run automated quality evaluations                | 45 min |
| 04 | [RAG with AI Search](./labs/04-rag-azure-search/README.md)     | Ground answers on your own data using Azure AI Search                 | 60 min |
| 05 | [Agent Service](./labs/05-agent-service/README.md)             | Build an agent with tools/function calling and run it                 | 45 min |

Work through them **in order** — each builds on concepts (and sometimes
resources) from the previous one.

---

## How to navigate

- **Presenting?** Start with the slide deck in [`slides/`](./slides/README.md).
  Render it to HTML or PDF with Marp.
- **Doing the labs?** Open each `labs/NN-*/README.md` and follow the numbered
  steps. Runnable Python files live alongside each lab's README.
- **Timing?** See [`AGENDA.md`](./AGENDA.md) for a suggested schedule.

---

## Troubleshooting quick reference

| Symptom                                              | Likely cause / fix                                                                 |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `DefaultAzureCredential failed to retrieve a token`  | Run `az login` and set the right subscription; ensure your account has RBAC roles. |
| `DeploymentNotFound` / 404 on model call             | The deployment name in `.env` must match exactly what you named it in the portal.  |
| `429 Too Many Requests`                              | You hit rate/quota limits — lower request rate or request more quota.              |
| `ModuleNotFoundError: azure.ai.projects`             | Activate your venv and re-run `pip install -r requirements.txt`.                   |
| Region/quota errors when deploying GPT-4o            | Try a different supported region (e.g. `eastus2`, `swedencentral`).                |

---

## Additional resources

- Azure AI Foundry documentation: <https://learn.microsoft.com/azure/ai-foundry/>
- Foundry portal: <https://ai.azure.com>
- `azure-ai-projects` SDK: <https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme>
- Azure AI Foundry Agent Service: <https://learn.microsoft.com/azure/ai-foundry/agents/>
- Model catalog: <https://ai.azure.com/explore/models>

## License

Released under the [MIT License](./LICENSE).
