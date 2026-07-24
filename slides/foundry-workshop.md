---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Building AI Applications with Azure AI Foundry'
footer: 'Hands-on Workshop · 2025/2026'
---

<!-- _class: lead -->
<!-- _paginate: false -->

# Building AI Applications with **Azure AI Foundry**

### A hands-on, one-day workshop

From zero to a deployed, grounded AI agent.

<!--
Speaker notes:
Welcome everyone. This deck accompanies five hands-on labs. By the end of today
you will have provisioned Foundry, called a model, engineered and evaluated
prompts, built a RAG pipeline over your own data, and shipped an agent with
function calling. Keep the portal (ai.azure.com) open in a second window.
-->

---

# Agenda

1. What is Azure AI Foundry?
2. Architecture — hubs, projects, connections
3. The model catalog
4. SDK overview
5. Prompt flow & evaluation
6. The RAG pattern
7. The Agent Service
8. Responsible AI
9. Wrap-up & next steps

<!--
Five labs are interleaved with these topics — see AGENDA.md for the timed
schedule. Slides set up each lab; the labs make it concrete.
-->

---

<!-- _class: lead -->

# 1. What is Azure AI Foundry?

<!--
Set the framing: Foundry is the unified successor to Azure AI Studio, bringing
model catalog, project workspace, prompt flow, evaluation, RAG, and agents into
one place.
-->

---

# What is Azure AI Foundry?

**A unified platform to design, customize, evaluate, and operate generative-AI
apps and agents at scale.**

- One portal: **ai.azure.com** + a family of **SDKs**
- **Model catalog**: Azure OpenAI, Microsoft, Meta, Mistral, Hugging Face, ...
- **Project-based** workspaces for building and collaboration
- Built-in **prompt flow**, **evaluation**, **RAG**, and the **Agent Service**
- Enterprise-grade **security, networking, and Responsible AI**

> Formerly **Azure AI Studio**. Foundry is the evolution, not a rename only —
> it adds first-class agents and a project resource model.

<!--
Emphasize "unified": before Foundry, teams stitched together Azure OpenAI,
Cognitive Search, ML workspaces, and custom eval code. Foundry integrates these.
-->

---

# Where Foundry fits

| Layer            | Examples                                                  |
| ---------------- | -------------------------------------------------------- |
| **Apps/Agents**  | Copilots, RAG chatbots, autonomous agents                |
| **Foundry**      | Catalog, projects, prompt flow, eval, Agent Service      |
| **Models**       | GPT-4o, o-series, Phi, Llama, Mistral, embeddings        |
| **Azure**        | Identity (Entra), networking, storage, AI Search, monitoring |

<!--
Foundry is the middle orchestration layer that turns raw models + Azure infra
into shippable AI applications.
-->

---

<!-- _class: lead -->

# 2. Architecture

## Hubs, projects, connections

---

# The resource hierarchy

- **Hub** — top-level collaboration & governance boundary. Holds shared
  settings: security, networking, connections, compute, and billing.
- **Project** — a workspace *inside* a hub where you build one solution. Gets its
  own **endpoint**, data, indexes, evaluations, and agents.
- **Connections** — secured references to external resources (Azure OpenAI,
  Azure AI Search, Storage, App Insights, Bing, ...).
- **Deployments** — a specific model made callable under a **deployment name**.

> **Foundry (2025) also offers a lighter "Foundry project" resource type** for
> agent-centric scenarios that doesn't require a full ML hub. Know both exist.

<!--
Analogy: Hub = the building (shared utilities, security desk); Project = your
office in it. Connections are like keys to shared rooms. Deployment names are
what you reference in code — a frequent source of 404s if they don't match.
-->

---

# What you'll do in Lab 01

- Create a **hub** + **project** in the Foundry portal
- Explore **connections** and roles (`Azure AI Developer`)
- Copy your **project endpoint** into `.env`
- Deploy your first model

```text
AZURE_AI_PROJECT_ENDPOINT=
  https://<resource>.services.ai.azure.com/api/projects/<project>
```

<!--
The project endpoint is the single most important value in .env — everything in
the labs authenticates against it with DefaultAzureCredential (keyless).
-->

---

<!-- _class: lead -->

# 3. The Model Catalog

---

# The model catalog

- **Thousands of models** from Azure OpenAI, Microsoft, Meta, Mistral,
  Cohere, Hugging Face, NVIDIA, and more.
- Two main deployment shapes:
  - **Serverless / Models-as-a-Service** — pay-per-token, no infra to manage.
  - **Managed compute** — dedicated GPUs you provision (for OSS/custom models).
- Filter by **task**, **provider**, **license**, and **capabilities**
  (tools, vision, JSON mode, context length).
- **Benchmarks** and **model cards** help you compare before committing.

<!--
Guidance: start with a serverless GPT-4o or GPT-4o-mini for chat, and
text-embedding-3-large for retrieval. Move to managed compute only when you need
a specific OSS model or data-residency guarantees.
-->

---

# Choosing a model

| Need                        | Reasonable default                     |
| --------------------------- | -------------------------------------- |
| General chat / reasoning    | `gpt-4o` (or `o`-series for hard reasoning) |
| Cheap/fast chat             | `gpt-4o-mini`                          |
| Embeddings (RAG)            | `text-embedding-3-large` (3072 dims)   |
| Small/on-device, fine-tune  | `Phi` family                           |
| Open-source / self-host     | `Llama`, `Mistral` (managed compute)   |

<!--
Don't over-optimize model choice early. Get a working pipeline, then evaluate
(Lab 03) and swap models to trade off cost vs. quality with data.
-->

---

<!-- _class: lead -->

# 4. SDK Overview

---

# The Foundry Python SDKs

| Package                   | Purpose                                                        |
| ------------------------- | ------------------------------------------------------------- |
| **`azure-ai-projects`**   | Unified project client: connections, datasets, **agents**     |
| **`azure-ai-inference`**  | Call deployed **chat** & **embedding** models                 |
| **`azure-ai-evaluation`** | Run evaluators (groundedness, relevance, safety, agents)      |
| **`azure-search-documents`** | Azure AI Search — indexes & vector/hybrid retrieval        |
| **`azure-identity`**      | `DefaultAzureCredential` — keyless auth via Entra ID          |

```bash
pip install azure-ai-projects azure-ai-inference \
            azure-ai-evaluation azure-search-documents azure-identity
```

<!--
These are the real, current package names — do not guess alternatives. The
project client is the entry point; it can hand you inference clients and hosts
the agents API.
-->

---

# Keyless auth — the recommended pattern

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import SystemMessage, UserMessage

project = AIProjectClient(
    endpoint=AZURE_AI_PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),   # uses `az login`, MI, VS Code...
)

chat = project.inference.get_chat_completions_client()
resp = chat.complete(
    model="gpt-4o",
    messages=[SystemMessage("You are concise."), UserMessage("Hello!")],
)
print(resp.choices[0].message.content)
```

<!--
No API keys in code. DefaultAzureCredential tries env vars, managed identity,
az login, and VS Code in order. This is what Labs 02–05 use.
-->

---

<!-- _class: lead -->

# 5. Prompt Flow & Evaluation

---

# Prompt engineering essentials

- **System prompt** sets role, tone, constraints, output format — highest leverage.
- **Few-shot examples** steer format and behaviour by demonstration.
- **Grounding** provides data so the model doesn't hallucinate (→ RAG).
- **Structured output** (JSON mode / schemas) for reliable downstream parsing.
- Control **temperature** and **max_tokens** for determinism vs. creativity.

<!--
Lab 03 compares a weak vs. improved prompt on the same question so the impact of
a good system prompt is visible, not theoretical.
-->

---

# Evaluation with `azure-ai-evaluation`

Measure quality **objectively** instead of eyeballing:

- **AI-assisted**: Groundedness, Relevance, Coherence, Fluency, Similarity
- **NLP metrics**: F1, BLEU, ROUGE, METEOR
- **Safety**: Violence, Hate/Unfairness, Self-harm, Sexual (via Content Safety)
- **Agent evaluators**: Intent Resolution, Tool Call Accuracy, Task Adherence

```python
from azure.ai.evaluation import RelevanceEvaluator, GroundednessEvaluator
```

> Run evaluations locally **or** push results to the portal's **Evaluation** tab
> to compare runs over time — a regression gate for prompts and models.

<!--
Evaluation closes the loop: build → measure → improve. In CI you can fail a
build if average groundedness drops below a threshold.
-->

---

<!-- _class: lead -->

# 6. The RAG Pattern

## Retrieval-Augmented Generation

---

# Why RAG?

- LLMs don't know your **private, recent, or proprietary** data.
- Fine-tuning is costly and stale; RAG is **cheap, current, and citable**.
- Retrieve relevant context at query time → **ground** the model on facts.

**The flow:**

```text
Docs → chunk → embed → vector index (Azure AI Search)
Query → embed → retrieve top-k → stuff into prompt → grounded answer + citations
```

<!--
Lab 04 builds every step explicitly with azure-search-documents + azure-ai-
inference embeddings, so the "Add your data" magic is demystified.
-->

---

# RAG on Azure AI Search

- **Chunking**: split docs into overlapping passages that fit the context window.
- **Embeddings**: `text-embedding-3-large` → 3072-dim vectors.
- **Index**: Azure AI Search field with an **HNSW** vector profile.
- **Retrieval**: vector, **keyword (BM25)**, or **hybrid** + **semantic ranker**.
- **Generation**: inject retrieved passages; instruct "answer only from context".

```python
vector_query = VectorizedQuery(vector=q_vec, k_nearest_neighbors=3,
                               fields="content_vector")
results = search_client.search(vector_queries=[vector_query])
```

<!--
Hybrid + semantic ranking usually beats pure vector search. Start simple
(vector), then add hybrid in the Lab 04 challenge.
-->

---

<!-- _class: lead -->

# 7. The Agent Service

---

# Azure AI Foundry Agent Service

- Managed **stateful** agents: the service tracks **threads**, **messages**, **runs**.
- **Tools** the agent can call:
  - **Function calling** (your Python functions)
  - **Code Interpreter**, **File Search**
  - **Azure AI Search** (grounding), **Bing** grounding, **OpenAPI** tools
- Built-in orchestration of the **tool-call loop** + observability/tracing.

```python
agent = project.agents.create_agent(
    model="gpt-4o", name="assistant",
    instructions="...", tools=function_tool.definitions)
```

> Preview API — the exact SDK surface can shift between `azure-ai-projects`
> betas; Lab 05 notes portable vs. version-specific patterns.

<!--
Agents = model + instructions + tools + memory, managed for you. Lab 05 wires a
custom get_weather function and drives the requires_action loop by hand, then
shows the auto-function-call shortcut.
-->

---

# The function-calling loop

```text
create agent ─► create thread ─► add user message ─► create run
                                                        │
                        ┌───────────────────────────────┘
                        ▼
                run.status == "requires_action"?
                        │ yes
          execute local function(s) ─► submit_tool_outputs
                        │
                        ▼  (repeat until completed)
                read final assistant message
```

<!--
The key state is requires_action: the model asks for a tool result, you run the
Python function, submit outputs, and the run resumes. This is the core mental
model for all tool use.
-->

---

<!-- _class: lead -->

# 8. Responsible AI

---

# Responsible AI on Foundry

- **Content Safety**: filters + severity levels for hate, violence, sexual, self-harm; **prompt shields** (jailbreak/indirect-injection), **groundedness detection**.
- **Evaluation**: safety & quality evaluators, red-teaming, adversarial simulators.
- **Observability**: tracing to **Application Insights**; monitor runs & tools.
- **Governance**: Entra ID RBAC, private networking, customer-managed keys, data residency.
- **Transparency**: model cards, and *your* responsibility for use-case fit + human oversight.

<!--
Responsible AI is not a checkbox — it spans build (evaluation), deploy (content
safety), and operate (monitoring). Encourage teams to add a safety evaluator to
their eval suite and enable tracing before production.
-->

---

<!-- _class: lead -->

# 9. Wrap-up

---

# What you built today

- ✅ Provisioned a **hub + project** and deployed a model
- ✅ Called GPT-4o with the **Foundry SDKs** (keyless)
- ✅ **Engineered & evaluated** prompts objectively
- ✅ Built a **RAG** pipeline over your own data with Azure AI Search
- ✅ Shipped an **agent** with **function calling**

<!--
Recap the arc: each lab added a capability. Participants now have a template
repo they can adapt to their own data and tools.
-->

---

# Next steps & resources

- **Azure AI Foundry docs**: <https://learn.microsoft.com/azure/ai-foundry/>
- **Foundry portal**: <https://ai.azure.com>
- **`azure-ai-projects`**: <https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme>
- **Agent Service**: <https://learn.microsoft.com/azure/ai-foundry/agents/>
- **Evaluation**: <https://learn.microsoft.com/azure/ai-foundry/how-to/develop/evaluate-sdk>

### Keep going
Add **hybrid + semantic** retrieval · attach **AI Search** to your agent ·
put **evaluation in CI** · enable **tracing** before production.

<!--
Point people to AGENDA.md and the lab READMEs for self-paced continuation.
Thank you — questions?
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

# Thank you!

### Questions?

Repo: the labs, slides, and `.env.example` are yours to keep and extend.
