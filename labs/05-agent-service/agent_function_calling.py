"""
Lab 05 - agent_function_calling.py

Build and run an agent with the **Azure AI Foundry Agent Service** using the
`azure-ai-projects` agents API. The agent is equipped with a custom **function
tool** (`get_weather`) and we handle the tool call loop end-to-end:

  1. Create an agent (name, model, instructions, tools)
  2. Create a conversation thread
  3. Post a user message
  4. Create a run and poll it
  5. When the run enters `requires_action`, execute the requested function(s)
     locally and submit the tool outputs
  6. Read back the agent's final message

Run from the repo root:
    python labs/05-agent-service/agent_function_calling.py

Required .env values:
    AZURE_AI_PROJECT_ENDPOINT   (keyless auth via DefaultAzureCredential)
    CHAT_MODEL_DEPLOYMENT       (a chat model that supports tools, e.g. gpt-4o)

-----------------------------------------------------------------------------
SDK-surface note (IMPORTANT):
    The Agent Service is in preview and the Python surface has shifted between
    `azure-ai-projects` betas. This sample targets the common shape where the
    agents operations hang off `project_client.agents` and tools are built with
    `azure.ai.agents.models` (e.g. FunctionTool, ToolSet). On some beta versions
    these live under `azure.ai.projects.models` instead, and the manual
    submit-tool-outputs loop can be replaced by passing a ToolSet with
    `enable_auto_function_calls(...)` so the SDK invokes your Python functions
    automatically. If an import fails, check the exact classes exported by your
    installed version:  python -c "import azure.ai.agents.models as m; print(dir(m))"
-----------------------------------------------------------------------------
"""

from __future__ import annotations

import json
import os
import sys
import time

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Tool/model types for the Agent Service. On some betas these are importable
# from `azure.ai.projects.models` instead of `azure.ai.agents.models`.
try:
    from azure.ai.agents.models import FunctionTool, ToolSet, RequiredFunctionToolCall
except ImportError:  # pragma: no cover - depends on installed beta
    from azure.ai.projects.models import FunctionTool, ToolSet, RequiredFunctionToolCall


# --------------------------------------------------------------------------
# 1. Define the local Python function(s) the agent may call.
# --------------------------------------------------------------------------
def get_weather(location: str, unit: str = "celsius") -> str:
    """Return the current weather for a location.

    This is a stubbed function returning canned data so the lab needs no
    external API key. Swap in a real weather API call for production.

    :param location: City name, e.g. "Seattle".
    :param unit: "celsius" or "fahrenheit".
    :return: A JSON string with the weather report.
    """
    fake_db = {
        "seattle": 14,
        "london": 11,
        "dubai": 41,
        "sydney": 22,
    }
    celsius = fake_db.get(location.strip().lower(), 20)
    temp = celsius if unit == "celsius" else round(celsius * 9 / 5 + 32)
    return json.dumps(
        {"location": location, "temperature": temp, "unit": unit, "conditions": "clear"}
    )


# Map of callable functions the agent is allowed to invoke.
FUNCTIONS = {get_weather}


def run_with_manual_tool_loop(project: AIProjectClient, deployment: str) -> int:
    """Create an agent and drive the run/tool-call loop by hand."""
    agents = project.agents

    # FunctionTool introspects the Python callables to build JSON tool schemas.
    function_tool = FunctionTool(functions=FUNCTIONS)

    # 1. Create the agent.
    agent = agents.create_agent(
        model=deployment,
        name="workshop-weather-agent",
        instructions=(
            "You are a helpful assistant. Use the get_weather tool when the user "
            "asks about the weather. Always state the unit in your answer."
        ),
        tools=function_tool.definitions,
    )
    print(f"Created agent: {agent.id}")

    try:
        # 2. Create a thread and 3. add a user message.
        thread = agents.threads.create()
        agents.messages.create(
            thread_id=thread.id,
            role="user",
            content="What's the weather like in Dubai in fahrenheit?",
        )
        print(f"Created thread: {thread.id}")

        # 4. Start a run.
        run = agents.runs.create(thread_id=thread.id, agent_id=agent.id)

        # 5. Poll and handle tool calls.
        while run.status in ("queued", "in_progress", "requires_action"):
            time.sleep(1)
            run = agents.runs.get(thread_id=thread.id, run_id=run.id)

            if run.status == "requires_action":
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for call in tool_calls:
                    if isinstance(call, RequiredFunctionToolCall):
                        name = call.function.name
                        args = json.loads(call.function.arguments or "{}")
                        print(f"  → agent calls {name}({args})")
                        # Look up and invoke the matching local function.
                        fn = next(f for f in FUNCTIONS if f.__name__ == name)
                        output = fn(**args)
                        tool_outputs.append({"tool_call_id": call.id, "output": output})

                agents.runs.submit_tool_outputs(
                    thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                )

        print(f"Run finished with status: {run.status}")
        if run.status == "failed":
            print(f"Run error: {run.last_error}")
            return 1

        # 6. Print the agent's final answer.
        messages = agents.messages.list(thread_id=thread.id)
        for message in messages:
            if message.role == "assistant":
                # text_messages holds the rendered text parts of the message.
                for part in message.text_messages:
                    print(f"\n=== Agent answer ===\n{part.text.value}")
                break
        return 0
    finally:
        # Clean up so repeated runs don't accumulate agents.
        agents.delete_agent(agent.id)
        print(f"Deleted agent: {agent.id}")


def run_with_auto_tools(project: AIProjectClient, deployment: str) -> int:
    """Alternative: let the SDK invoke your Python functions automatically.

    On betas that support it, a ToolSet with auto function calls removes the
    manual `requires_action` loop entirely.
    """
    agents = project.agents
    toolset = ToolSet()
    toolset.add(FunctionTool(functions=FUNCTIONS))

    # Tell the SDK it may call the local Python functions itself.
    agents.enable_auto_function_calls(toolset)

    agent = agents.create_agent(
        model=deployment,
        name="workshop-weather-agent-auto",
        instructions="Use get_weather for weather questions.",
        toolset=toolset,
    )
    try:
        thread = agents.threads.create()
        agents.messages.create(
            thread_id=thread.id, role="user", content="Weather in Sydney?"
        )
        # create_and_process runs the loop (including tool calls) to completion.
        run = agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Auto run status: {run.status}")
        messages = agents.messages.list(thread_id=thread.id)
        for message in messages:
            if message.role == "assistant":
                for part in message.text_messages:
                    print(f"\n=== Agent answer (auto) ===\n{part.text.value}")
                break
        return 0
    finally:
        agents.delete_agent(agent.id)


def main() -> int:
    load_dotenv()

    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip()
    deployment = os.getenv("CHAT_MODEL_DEPLOYMENT", "gpt-4o").strip()
    if not endpoint or endpoint.startswith("https://<"):
        print("❌ Set AZURE_AI_PROJECT_ENDPOINT in .env (see Lab 01).")
        return 1

    project = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # The manual loop is the most portable across preview versions.
    return run_with_manual_tool_loop(project, deployment)

    # To try the automatic variant instead, comment the line above and use:
    # return run_with_auto_tools(project, deployment)


if __name__ == "__main__":
    sys.exit(main())
