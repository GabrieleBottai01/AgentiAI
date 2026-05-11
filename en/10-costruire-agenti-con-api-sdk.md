# 10. Building Custom Agents with API and SDK

Now we build. In this chapter we'll make an agent from scratch in Python, with prompt caching, tools, error handling and best practices. By the end you'll have a template you can extend for most use cases.

## 10.1 Setup

We'll use the **Anthropic SDK** as the primary SDK. Everything translates with small differences to OpenAI SDK; we'll mark important differences.

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

(On [console.anthropic.com](https://console.anthropic.com) you create an API key. Same on [platform.openai.com](https://platform.openai.com) for OpenAI.)

## 10.2 Hello, agent

The "single call" level:

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hi, who are you?"}
    ]
)

print(response.content[0].text)
```

This is a chatbot, not an agent — no loop, no tools. Let's build the real agent.

## 10.3 A minimal, runnable agent

```python
"""
Minimal agent: has 2 tools (calculator + current time),
loops until the model stops calling tools.
"""

from anthropic import Anthropic
from datetime import datetime
import json

client = Anthropic()
MODEL = "claude-opus-4-7"

# 1. Tool definition
TOOLS = [
    {
        "name": "calculator",
        "description": "Runs a Python arithmetic expression. Use ONLY for numerical calculations (e.g. '2+2', '15 * 23 / 4'). Not for text or generic code.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Valid arithmetic expression in Python"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "current_time",
        "description": "Returns current date and time in ISO format. Use when the user asks 'what time', 'what day', or for timestamps.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

# 2. Tool implementation
def calculator(expression: str) -> str:
    try:
        # WARNING: eval is dangerous. In production use a safe parser.
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"error: {e}"

def current_time() -> str:
    return datetime.now().isoformat()

TOOL_FUNCS = {
    "calculator": calculator,
    "current_time": current_time,
}

# 3. The agent loop
def run_agent(user_message: str, max_iterations: int = 10) -> str:
    messages = [{"role": "user", "content": user_message}]

    for step in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system="You are a precise assistant. Use tools when needed. Concise responses.",
            tools=TOOLS,
            messages=messages,
        )

        # Update history with the response
        messages.append({"role": "assistant", "content": response.content})

        # If no tools called, we're done
        if response.stop_reason != "tool_use":
            text_blocks = [b for b in response.content if b.type == "text"]
            return text_blocks[-1].text if text_blocks else "(no response)"

        # Run requested tools
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                func = TOOL_FUNCS.get(block.name)
                if not func:
                    result = f"error: tool '{block.name}' does not exist"
                else:
                    result = func(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})

    return "Iteration limit reached."


# Try
if __name__ == "__main__":
    print(run_agent("How many minutes have passed since midnight until now?"))
```

Run this file. The agent:
1. Sees the question.
2. Calls `current_time()`.
3. Thinks: "now I have current time, I need to calculate minutes since midnight".
4. Calls `calculator("...")` with the right expression.
5. Answers.

Three LLM steps, two tools. **This is an agent**.

## 10.4 Prompt caching: the trick to learn immediately

When the system prompt is large (hundreds or thousands of tokens), paying it on every call is a waste. Anthropic API's **prompt caching** lets you load the system prompt **once** and reuse it at ~10% cost on subsequent calls (within 5 minutes).

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,   # e.g. 8000 tokens
            "cache_control": {"type": "ephemeral"}  # ← cache!
        }
    ],
    tools=TOOLS,
    messages=messages,
)
```

For agents that do many turns with the same system prompt, it's a huge saving. **Always on** in production on any non-trivial system prompt.

Details:
- TTL: 5 minutes from last read. Renews on every hit.
- Granularity: per block. You can mark the system prompt as cached and tools as non-cached.
- Tool definitions can also be cached.

OpenAI has an equivalent automatic mechanism (cache hit after the first 1024 common tokens).

## 10.5 Streaming

For better UX, enable streaming. The model returns tokens as it produces them.

```python
with client.messages.stream(
    model=MODEL,
    max_tokens=2048,
    messages=[{"role": "user", "content": "Explain neural networks"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()
```

In agents with tools, streaming is handled with event-based handlers (more complex, but useful to give realtime feedback to the user).

## 10.6 Structured outputs (JSON mode)

If you want the model to respond in JSON conforming to a schema, use the "tool with single tool" pattern or dedicated features.

OpenAI has `response_format={"type": "json_schema", "json_schema": {...}}`, guarantees valid JSON.

Anthropic doesn't yet have a strict mode but the "single tool" pattern is equivalent:

```python
extract_tool = {
    "name": "extract_person",
    "description": "Extracts info about a person from text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "occupation": {"type": "string"}
        },
        "required": ["name"]
    }
}

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=[extract_tool],
    tool_choice={"type": "tool", "name": "extract_person"},  # ← force use
    messages=[{"role": "user", "content": "Mario, 42, engineer..."}]
)

extracted = response.content[0].input  # already valid dict
```

Forced `tool_choice` guarantees the model calls that tool, and parameters are validated against the schema.

## 10.7 Retry, timeout, errors

In production the network drops, APIs return 429 (rate limit) or 503. Best practice:

```python
from anthropic import APIError, APIConnectionError, RateLimitError
import time

def call_with_retry(fn, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return fn()
        except RateLimitError:
            wait = 2 ** attempt
            print(f"rate limit, retry in {wait}s")
            time.sleep(wait)
        except APIConnectionError:
            time.sleep(1)
        except APIError as e:
            if e.status_code >= 500 and attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    raise RuntimeError("max retries reached")
```

Useful client config:

```python
client = Anthropic(
    timeout=30.0,
    max_retries=3,    # SDK already has built-in exponential retry
)
```

## 10.8 Infinite loops: how to prevent them

Three standard protections:

1. **Iteration limit**: already seen, never above 25-30.
2. **Cumulative token limit**: track the total, stop at threshold.
3. **Loop detection**: if the agent calls the same tool with the same arguments 3 times, stop and log.

```python
seen_calls = set()
for block in response.content:
    if block.type == "tool_use":
        signature = (block.name, json.dumps(block.input, sort_keys=True))
        if signature in seen_calls:
            return "Loop detected, stopping the agent."
        seen_calls.add(signature)
```

## 10.9 OpenAI SDK: key differences

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "...",
            "parameters": {...}  # JSON Schema
        }
    }]
)

# Result accessible at:
# response.choices[0].message.tool_calls
# response.choices[0].finish_reason  ('tool_calls', 'stop', ...)
```

Differences from Anthropic:
- Tool wrapped in `{"type": "function", "function": {...}}`.
- `parameters` instead of `input_schema`.
- Response in `choices[0].message.tool_calls` (list of tool calls).
- `tool_call.function.arguments` is a JSON string, must be parsed.
- Tool result goes as message role=`"tool"` with `tool_call_id`.

If you want provider-agnostic code, use **LiteLLM** (Ch. 11) which abstracts the differences.

## 10.10 Claude Agent SDK

For complex agents with harness similar to Claude Code (file ops, bash, todo, MCP), Anthropic offers the **Claude Agent SDK**:

```python
from claude_agent_sdk import ClaudeAgent

agent = ClaudeAgent(
    system_prompt="You are a developer agent.",
    allowed_tools=["read_file", "write_file", "bash"],
    working_directory="./my-project"
)

result = await agent.run("Add a /health endpoint to the FastAPI app")
```

It gives you for free: filesystem management, command execution, prompt caching, automatic compaction. Worth it for serious coding agents.

## 10.11 Costs: understanding and optimizing

Costs are calculated on tokens (input + output). Typical 2026 rates (varies, always check):

| Model | Input ($/M tok) | Output ($/M tok) |
|---|---|---|
| Claude Opus 4.7 | ~15 | ~75 |
| Claude Sonnet 4.6 | ~3 | ~15 |
| Claude Haiku 4.5 | ~0.80 | ~4 |
| GPT-5 | ~10 | ~40 |
| GPT-5 Mini | ~0.25 | ~2 |

Tricks to save:

1. **Prompt caching** on system prompt → -90% on repeated input.
2. **Smaller models** where they suffice. Often Haiku/Mini do 80% of tasks at 5% of cost.
3. **Truncate tool results** to what's actually needed.
4. **History compaction** when long.
5. **Batch API** for non-realtime tasks → -50%.
6. **Iteration and token caps** to prevent expensive loops.

ALWAYS set a **budget alert** on the API console when going to production.

## 10.12 Final example: research agent

Putting it all together in an agent that searches the web and produces a brief.

```python
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic

client = Anthropic()

def web_search(query: str) -> str:
    """Fake: in reality would call SerpAPI / Tavily / Brave Search API."""
    return f"[results for: {query}]"

def fetch_url(url: str) -> dict:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)[:5000]
        return {"ok": True, "content": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web. Use for up-to-date facts or general searches.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Downloads and extracts text from a URL. Use to read specific sources.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    }
]

TOOL_FUNCS = {"web_search": web_search, "fetch_url": fetch_url}

SYSTEM = """You are a research agent. Procedure:
1. Understand the question. If ambiguous, ask one clarifying question in text.
2. Do 1-3 targeted web searches.
3. For the 2-3 most promising sources, read them with fetch_url.
4. Synthesize a 200-300 word brief CITING the sources.
5. If info isn't enough, say so instead of inventing.

Stop when you have a satisfactory brief."""

def research(question: str, max_iters: int = 15) -> str:
    messages = [{"role": "user", "content": question}]
    for step in range(max_iters):
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return next(b.text for b in resp.content if b.type == "text")
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out = TOOL_FUNCS[b.name](**b.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": b.id,
                    "content": str(out),
                })
        messages.append({"role": "user", "content": results})
    return "Iterations exhausted."

print(research("What is the state of open-source AI models in 2026?"))
```

200 lines, a real research agent. From here add: history persistence, retry, observability (Langfuse/LangSmith), real web search (SerpAPI or Tavily).

## 10.13 Key takeaways

- **The loop is ~50 lines.** All the value is in the tools and prompts.
- **Prompt caching** for large system prompts: huge savings.
- **Iteration limit + loop detection** to not spiral.
- **Structured tool result (ok/error)** so the agent can recover.
- **Streaming** for UX, **forced tool_choice** for structured output.
- **Small model where enough**, big model only where needed.
- **Budget alert** in production, always.

## 10.14 Common mistakes

- **No cache**: you pay 10x the necessary on large system prompts.
- **No iteration limit**: one night you realize you've burned €50.
- **Tool returning 100KB of HTML**: saturated context, exploding costs.
- **Exceptions in tools** instead of structured error string: the agent breaks.
- **`eval` as calculator**: in production opens huge security holes.
- **Leaving "Opus" model always**: try Sonnet/Haiku, often they work fine.

---

Building from scratch is educational and flexible. For more complex pipelines, frameworks give a higher abstraction. Let's see the main ones.

→ [Chapter 11 — Frameworks: LangChain, AutoGen, CrewAI](11-framework-langchain-autogen-crewai.md)
