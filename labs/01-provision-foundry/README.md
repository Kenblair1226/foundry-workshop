# Lab 01 — Provision an Azure AI Foundry Hub + Project

## Objective

Create the foundational Azure AI Foundry resources you'll use throughout the
workshop — a **hub**, a **project**, and your first **model deployment** — and
get comfortable navigating the [Foundry portal](https://ai.azure.com).

By the end you will understand the Foundry resource hierarchy and have a working
project endpoint recorded in your `.env` file.

## Prerequisites

- Completed the [root setup](../../README.md#one-time-setup) (`az login`, venv, deps).
- An Azure subscription with permission to create resources.
- Azure OpenAI quota for GPT-4o (or GPT-4o-mini) in a supported region.

## Estimated time

**45 minutes**

## Key concepts

| Concept        | What it is                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------ |
| **Hub**        | The top-level, team-shared collaboration resource. Holds shared security, connections (e.g. to storage, Azure AI Search, key vault), and compute. One hub can host many projects. |
| **Project**   | A workspace *inside* a hub where you build a specific app: deployments, prompt flows, evaluations, agents, indexes, and data all live here. |
| **Connection**| A secure, reusable link to an external resource (Azure OpenAI, AI Search, Blob Storage, etc.), shared from the hub. |
| **Model catalog** | The gallery of foundation models you can deploy (Azure OpenAI, Microsoft, Meta, Mistral, Hugging Face…). |
| **Deployment**| A specific model made callable at an endpoint, with its own name, capacity (TPM), and version. |

> **Note (2025+):** Foundry also supports a newer **"Foundry project"** type
> hosted directly on an **Azure AI Foundry resource** (without a classic hub),
> which is the recommended path for the Agent Service. This lab uses the
> **hub-based** project because it exposes the full workshop feature set
> (prompt flow, hub connections, shared compute). Lab 05 notes where a Foundry
> (resource-based) project is preferable.

---

## Steps

### 1. Open the Foundry portal

1. Browse to **<https://ai.azure.com>** and sign in with your Azure account.
2. In the top-right, confirm the correct **directory/tenant** is selected.

### 2. Create a hub

1. Click **Management center** (bottom-left nav) → **All resources** →
   **+ New** → **New hub**. *(Alternatively: from the home page choose
   **+ Create** → **Hub**.)*
2. Fill in:
   - **Hub name:** `foundry-workshop-hub`
   - **Subscription:** your subscription
   - **Resource group:** create new → `rg-foundry-workshop`
   - **Location/Region:** a region with GPT-4o quota, e.g. **East US 2** or **Sweden Central**
   - **Connect Azure AI Services / Azure OpenAI:** let it **create a new** AI Services resource (this provides Azure OpenAI + Content Safety + Speech + Vision under one connection).
3. Click **Next** → review → **Create**. Provisioning takes ~2–3 minutes.

### 3. Create a project inside the hub

1. Once the hub is ready, click **+ New project** (or Management center →
   your hub → **New project**).
2. **Project name:** `workshop-project`
3. Confirm the **hub** is `foundry-workshop-hub`.
4. Click **Create**.

### 4. Explore the portal

Spend a few minutes clicking through the left navigation of your project:

- **Overview** — project endpoint, keys, and connected resources.
- **Model catalog** — browse available models; note the filters (collection,
  inference task, deployment options).
- **Models + endpoints** — where your deployments will appear.
- **Playgrounds** — chat, assistants, and images playgrounds for quick testing.
- **Prompt flow** — visual authoring for LLM workflows (used in Lab 03).
- **Evaluation** — automated quality/safety evaluations (Lab 03).
- **Management center** — hub/project settings, connections, and RBAC.

### 5. Deploy your first model

1. Go to **Model catalog**, search for **`gpt-4o`**, and open the model card.
2. Click **Deploy** → **Deploy to a real-time endpoint** (or **Deploy**).
3. Settings:
   - **Deployment name:** `gpt-4o` (keep it simple — this becomes `CHAT_MODEL_DEPLOYMENT`)
   - **Deployment type:** *Global Standard* (or *Standard*)
   - **Model version:** the default recommended version
   - **Tokens per minute rate limit:** leave default (e.g. 30K–50K TPM)
4. Click **Deploy** and wait until status is **Succeeded**.
5. Repeat for an embedding model you'll need in Lab 04:
   - Search **`text-embedding-3-large`** → **Deploy** → name it `text-embedding-3-large`.

### 6. Record your connection details in `.env`

1. Go to the project **Overview** page.
2. Copy the **project endpoint** (looks like
   `https://<resource>.services.ai.azure.com/api/projects/workshop-project`).
3. Open `.env` at the repo root and set:

   ```dotenv
   AZURE_AI_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/workshop-project"
   CHAT_MODEL_DEPLOYMENT="gpt-4o"
   EMBEDDING_MODEL_DEPLOYMENT="text-embedding-3-large"
   ```

### 7. Verify with the check script

From the repo root (venv active):

```bash
python labs/01-provision-foundry/verify_setup.py
```

## Expected output

```
✅ .env loaded
✅ AZURE_AI_PROJECT_ENDPOINT is set: https://xxx.services.ai.azure.com/api/projects/workshop-project
✅ DefaultAzureCredential acquired a token
✅ Connected to project. Deployments found:
   - gpt-4o                 (chat completion)
   - text-embedding-3-large (embeddings)
🎉 Lab 01 complete — you're ready for Lab 02!
```

*(The exact list depends on what you deployed. As long as your chat deployment
appears and no errors are raised, you're good.)*

---

## Troubleshooting

| Problem                                                    | Fix                                                                                              |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Can't create a hub — "not authorized"                      | You need `Owner`/`Contributor` on the subscription or resource group. Ask your admin.           |
| GPT-4o not available / quota error at deploy               | Switch the hub region (e.g. `swedencentral`) or deploy `gpt-4o-mini`. Check quota in Management center → Quota. |
| `verify_setup.py` → `DefaultAzureCredential failed`        | Run `az login` again and `az account set --subscription <id>`.                                  |
| `verify_setup.py` → 403 / authorization error              | Assign yourself the **Azure AI Developer** role on the project's resource group.                |
| Endpoint copied but script says "not set"                  | Ensure there are no stray quotes/spaces and that you saved `.env` at the **repo root**.         |

---

## Challenge / Extension

1. **Explore connections:** In Management center → **Connections**, inspect the
   auto-created Azure AI Services connection. Add a new connection to an Azure
   Blob Storage account (you'll reuse this idea in Lab 04).
2. **RBAC:** Assign a teammate the **Azure AI Developer** role on the project and
   confirm they can see (but not delete the hub) resources.
3. **CLI provisioning:** Reproduce the hub + project creation using the Azure
   CLI `az ml` extension or Bicep, so the whole setup is reproducible as
   infrastructure-as-code. (Hint: `az extension add -n ml`.)
