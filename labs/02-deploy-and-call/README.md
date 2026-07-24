# Lab 02 — Deploy a Model and Call It from Python

## Objective

Call your deployed GPT-4o model from Python two ways:

1. Using the **`azure-ai-projects`** SDK (`AIProjectClient`) — the recommended,
   project-centric entry point that gives you an authenticated inference client.
2. Using the **`azure-ai-inference`** SDK directly (`ChatCompletionsClient`) —
   the lower-level model-inference API, including **streaming**.

## Prerequisites

- Completed **Lab 01** (hub, project, `gpt-4o` deployment, `.env` populated).
- Repo dependencies installed, `az login` done.

## Estimated time

**60 minutes**

## Key concepts

- **`AIProjectClient`** is your gateway to a Foundry project. From it you can get
  an OpenAI-compatible / inference client via
  `project.inference.get_chat_completions_client()` (or `.get_azure_openai_client()`),
  so you don't manage endpoints/keys by hand.
- **`ChatCompletionsClient`** (from `azure-ai-inference`) speaks the unified Azure
  AI model-inference protocol — the same code works across many catalog models,
  not just Azure OpenAI.
- **Messages**: `SystemMessage`, `UserMessage`, `AssistantMessage` structure the
  conversation. **Parameters** like `temperature`, `max_tokens`, and `top_p`
  control generation.

---

## Steps

### 1. Confirm your `.env`

```dotenv
AZURE_AI_PROJECT_ENDPOINT="https://<resource>.services.ai.azure.com/api/projects/workshop-project"
CHAT_MODEL_DEPLOYMENT="gpt-4o"

# Only needed for the direct-inference (api key) sample:
AZURE_INFERENCE_ENDPOINT="https://<resource>.services.ai.azure.com/models"
AZURE_INFERENCE_API_KEY="<key from Models + endpoints>"
```

> The `AZURE_INFERENCE_ENDPOINT` and key are on your project's
> **Models + endpoints → <deployment> → Endpoint** tab (Target URI + Key).

### 2. Run the project-client chat sample

```bash
python labs/02-deploy-and-call/chat_with_project_client.py
```

This authenticates with `DefaultAzureCredential` (no keys), gets a chat client
from the project, and sends a single prompt.

### 3. Run the streaming sample

```bash
python labs/02-deploy-and-call/chat_streaming.py
```

Watch tokens stream to your console as they are generated.

### 4. Run the direct inference (API-key) sample

```bash
python labs/02-deploy-and-call/inference_client_apikey.py
```

This uses `azure-ai-inference` with `AzureKeyCredential` — handy when you want a
self-contained script that only needs an endpoint + key.

### 5. Experiment

- Change the **system prompt** to give the assistant a persona.
- Adjust **`temperature`** (0.0 = deterministic, 1.0 = creative) and observe.
- Add a multi-turn conversation by appending `AssistantMessage` +
  `UserMessage` pairs.

---

## Expected output

`chat_with_project_client.py`:

```
> Prompt: Explain what Azure AI Foundry is in one sentence.
Azure AI Foundry is a unified Microsoft platform for building, evaluating,
deploying, and managing generative-AI applications and agents, combining a
model catalog, project workspaces, prompt flow, RAG, and an Agent Service.

Tokens — prompt: 24, completion: 41, total: 65
```

`chat_streaming.py` prints the answer progressively, then a done marker.

---

## Troubleshooting

| Problem                                     | Fix                                                                                     |
| ------------------------------------------- | --------------------------------------------------------------------------------------- |
| `DeploymentNotFound` (404)                  | `CHAT_MODEL_DEPLOYMENT` must exactly match the portal deployment name.                   |
| `401`/`403` on the project client           | Run `az login`; ensure **Azure AI Developer** role on the project resource group.       |
| `401` on the API-key sample                 | Wrong/expired `AZURE_INFERENCE_API_KEY`, or endpoint missing the `/models` suffix.      |
| `429 Too Many Requests`                     | You exceeded the TPM rate limit — wait, retry, or raise quota in the portal.            |
| `get_chat_completions_client` AttributeError| Update the SDK (`pip install -U azure-ai-projects azure-ai-inference`); API surface for `.inference` evolves across preview versions — see comments in the sample for the fallback. |

---

## Challenge / Extension

1. **Multi-turn chat loop:** Wrap the call in a `while True:` REPL that keeps
   conversation history so the model remembers previous turns.
2. **JSON mode:** Ask the model to return structured JSON (set
   `response_format` to a JSON object) and parse it with `json.loads`.
3. **Compare models:** Deploy `gpt-4o-mini` and compare latency, cost, and
   answer quality against `gpt-4o` for the same prompt.
4. **Token budget:** Add a `max_tokens` cap and observe truncation behaviour.
