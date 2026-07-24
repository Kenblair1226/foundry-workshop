# Lab 05 — Build an Agent with the Azure AI Foundry Agent Service

## Objective

Create an **agent** with the **Azure AI Foundry Agent Service** and give it a
**custom function tool**. You'll drive the full agent loop — create agent →
thread → message → run — and handle **function calling**: when the model decides
it needs your tool, your code executes the function and returns the result so the
agent can finish its answer.

The Agent Service manages state (threads, messages, runs), tool orchestration,
and integrates with tools like Code Interpreter, File Search, Azure AI Search,
Bing grounding, OpenAPI tools, and **your own functions**.

## Prerequisites

- Completed **Lab 02** (project endpoint working, `az login` done).
- A **tool-capable chat deployment** (e.g. `gpt-4o`) in your Foundry project.
- `.env` with `AZURE_AI_PROJECT_ENDPOINT` and `CHAT_MODEL_DEPLOYMENT`.
- Your account has the **`Azure AI Developer`** role on the project (needed to
  create agents).

> The Agent Service is in **preview**. Package: `azure-ai-projects` (agents
> operations are exposed via `project_client.agents`; tool models come from
> `azure-ai-agents`, installed as a dependency). See the SDK-surface note at the
> top of `agent_function_calling.py` — the exact import path can differ between
> beta versions.

## Estimated time

**45 minutes**

## Key concepts

| Concept              | Description                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------------- |
| **Agent**            | A configured model + instructions + tools that the service persists and orchestrates.           |
| **Thread**           | A stateful conversation; you append messages and the service tracks history.                    |
| **Run**              | An execution of the agent against a thread; it may pause to request tool calls.                 |
| **Function tool**    | A Python callable exposed to the model; the model emits arguments, you execute and return output.|
| **requires_action**  | The run status meaning "the model wants a tool result before it can continue".                  |
| **ToolSet (auto)**   | An SDK helper that can invoke your Python functions automatically, hiding the manual loop.       |

---

## Steps

### 1. Confirm your environment

Reuse the values from earlier labs:

```dotenv
AZURE_AI_PROJECT_ENDPOINT="https://<your-foundry-resource>.services.ai.azure.com/api/projects/<your-project>"
CHAT_MODEL_DEPLOYMENT="gpt-4o"
```

Verify auth:

```bash
az login
```

### 2. Read the tool function

Open [`agent_function_calling.py`](./agent_function_calling.py) and look at
`get_weather(location, unit)`. It's a stub returning canned JSON so the lab needs
no external API key. The `FunctionTool` introspects its signature + docstring to
build the JSON schema the model sees.

### 3. Run the agent

```bash
python labs/05-agent-service/agent_function_calling.py
```

The script walks the full lifecycle:

1. **Create agent** with the model, instructions, and the `get_weather` tool.
2. **Create thread** and post the user message
   *"What's the weather like in Dubai in fahrenheit?"*.
3. **Create run** and poll it.
4. On **`requires_action`**, read the requested tool call(s), execute
   `get_weather` locally, and **submit tool outputs**.
5. Read back the agent's final assistant message.
6. **Delete the agent** to keep your project tidy.

### 4. Understand the tool-call loop

The heart of function calling is the `while` loop in
`run_with_manual_tool_loop`. When `run.status == "requires_action"`, the service
hands you `run.required_action.submit_tool_outputs.tool_calls`. You match each
call to a local function, invoke it, and call `submit_tool_outputs`. The run then
continues until it reaches `completed`.

### 5. (Optional) Let the SDK auto-invoke your functions

Betas that support `enable_auto_function_calls(toolset)` +
`runs.create_and_process(...)` remove the manual loop entirely — the SDK calls
your Python functions for you. See `run_with_auto_tools()` and switch to it at
the bottom of `main()`.

### 6. Inspect the agent in the portal

While a run is in flight (or before the delete), open **Agents** in the
[Foundry portal](https://ai.azure.com) to see the agent, its threads, and run
traces.

---

## Expected output

```
Created agent: asst_abc123...
Created thread: thread_xyz789...
  → agent calls get_weather({'location': 'Dubai', 'unit': 'fahrenheit'})
Run finished with status: completed

=== Agent answer ===
The weather in Dubai is currently about 106°F with clear conditions.

Deleted agent: asst_abc123...
```

*(Exact wording varies — the model paraphrases the tool result.)*

---

## Troubleshooting

| Problem                                                        | Fix                                                                                                    |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `ImportError: cannot import name 'FunctionTool'`               | Your beta exports it elsewhere. Try `from azure.ai.projects.models import ...` or run `python -c "import azure.ai.agents.models as m; print(dir(m))"`. |
| `AttributeError: 'AIProjectClient' object has no attribute 'agents'` | Update: `pip install -U azure-ai-projects azure-ai-agents`. Older betas used a different accessor.     |
| `403 Forbidden` creating the agent                             | Grant your identity the **Azure AI Developer** role on the project/resource group.                     |
| Run stays `requires_action` forever                            | You must call `submit_tool_outputs` with a `tool_call_id` matching each requested call.                |
| Run status `failed` with model error                           | The deployment may not support tools — use a tools-capable model like `gpt-4o`.                         |
| Agents pile up in the portal                                   | The script deletes its agent in a `finally` block; delete stragglers manually under **Agents**.        |

---

## Challenge / Extension

1. **Add a second tool:** Add e.g. `convert_currency(amount, from_ccy, to_ccy)`
   and ask a question that requires both tools in one run.
2. **Built-in tools:** Attach the **Code Interpreter** tool and ask the agent to
   compute something, or **File Search** over uploaded files.
3. **RAG agent:** Wire the **Azure AI Search** tool to the index you built in
   Lab 04 so the agent grounds answers on your data automatically.
4. **Streaming:** Use the streaming run API to render tokens and tool events live.
5. **Observability:** Enable tracing to Application Insights
   (`APPLICATIONINSIGHTS_CONNECTION_STRING`) and inspect the run spans.
6. **Evaluate the agent:** Use `azure-ai-evaluation`'s agent evaluators
   (e.g. *Intent Resolution*, *Tool Call Accuracy*, *Task Adherence*) to score it.
