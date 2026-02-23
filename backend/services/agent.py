import asyncio
import contextvars
import inspect
import json
from typing import AsyncGenerator, Optional, List

from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import ReActAgent, AgentStream
from llama_index.core.tools import FunctionTool
from fastmcp import Client

import backend.config as config
from backend.services.files import save_generated_test
from backend.system_prompt import system_prompt as sys_p

# ----------- LLM -----------
llm = Ollama(
    model=config.OLLAMA_MODEL,
    base_url=config.OLLAMA_BASE_URL,
    request_timeout=300.0,  # Increased timeout for complex sites
)

# ----------- Progress bus -----------
PROGRESS_QUEUE_VAR = contextvars.ContextVar("progress_queue", default=None)

def _normalize_label(label: str) -> str:
    return (label or "").strip().lower().replace(" ", "-")

def _ndjson_event(event_type: str, payload: dict) -> str:
    return json.dumps({"type": event_type, **payload}, ensure_ascii=False) + "\n"

def update_progress(label: str, state: str = "begin", extra: Optional[str] = None):
    q: asyncio.Queue | None = PROGRESS_QUEUE_VAR.get()
    if q is None: return
    payload = {"label": _normalize_label(label), "state": state}
    if extra is not None: payload["extra"] = extra
    try:
        q.put_nowait(payload)
    except Exception: pass

# ----------- Tools -----------
def _wrap_mcp_tools(mcp_client, mcp_tools) -> List[FunctionTool]:
    wrapped = []
    for tool in mcp_tools:
        name = tool.name
        description = tool.description or ""
        input_schema = tool.inputSchema or {}

        async def _call(name1=name, **kwargs):
            try:
                # Log to terminal for debugging
                print(f"DEBUG: Calling Tool {name1} with {kwargs}")
                safe_kwargs = {k: str(v) if not isinstance(v, (dict, list)) else v for k, v in kwargs.items()}
                res = await mcp_client.call_tool(name=name1, arguments=safe_kwargs)
                return str(res)
            except Exception as e:
                return f"Error calling tool {name1}: {str(e)}"

        wrapped.append(
            FunctionTool.from_defaults(
                name=name,
                description=description + " " + str(input_schema),
                fn=_call,
            )
        )
    return wrapped

async def save_test_tool_fn(test: str) -> str:
    update_progress("saving script", "begin")
    result = save_generated_test(test)
    if "saved successfully" in str(result).lower():
        update_progress("saving script", "complete")
    else:
        update_progress("saving script", "fail")
    return str(result)

save_generated_test_tool = FunctionTool.from_defaults(
    name="save_generated_test",
    description="Save the final generated Playwright test script to the filesystem. Call this only AFTER you have verified the steps in the browser.",
    fn=save_test_tool_fn,
)

# ----------- Orchestrator -----------
async def orchestrator(user_query: str) -> AsyncGenerator[str, None]:
    """Single-level ReAct Agent that streams everything."""
    progress_queue: asyncio.Queue = asyncio.Queue()
    PROGRESS_QUEUE_VAR.set(progress_queue)

    update_progress("started", "begin")
    
    # Start MCP Browser
    mcp_config = {"mcpServers": {"playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}}}
    client = Client(mcp_config)

    try:
        async with client:
            update_progress("generating script", "begin")
            
            # Fetch tools
            mcp_tools = await client.list_tools()
            tools = _wrap_mcp_tools(client, mcp_tools) + [save_generated_test_tool]
            
            agent = ReActAgent(
                llm=llm,
                tools=tools,
                system_prompt=sys_p,
            )

            # Start streaming
            handler = agent.run(user_query, max_iterations=100)
            
            async for event in handler.stream_events():
                # Yield progress updates if any
                while not progress_queue.empty():
                    payload = progress_queue.get_nowait()
                    percent_map = {
                        ("started", "begin"): 5,
                        ("generating script", "begin"): 10,
                        ("saving script", "begin"): 85,
                        ("saving script", "complete"): 95,
                        ("done", "complete"): 100,
                    }
                    payload["percent"] = percent_map.get((payload["label"], payload["state"]), 50)
                    yield _ndjson_event("status", payload)

                # Yield agent thoughts/actions
                if isinstance(event, AgentStream) and getattr(event, "delta", None):
                    yield _ndjson_event("delta", {"text": event.delta})
                
                # If it's a tool call, we want the user to see it
                # LlamaIndex stream_events handles printing actions/observations as deltas usually
            
            final_response = str(await handler)
            update_progress("done", "complete")
            
            # Final flush
            while not progress_queue.empty():
                payload = progress_queue.get_nowait()
                yield _ndjson_event("status", payload)
                
            yield _ndjson_event("final", {"message": "Agent completed.", "text": final_response})

    except Exception as e:
        import traceback
        print(f"ORCHESTRATOR ERROR: {traceback.format_exc()}")
        yield _ndjson_event("error", {"message": str(e)})