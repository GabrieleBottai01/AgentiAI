# 6. Tool Use and Function Calling

Tools are what turn an LLM into an agent. Without tools, it talks. With tools, it acts.

## 6.1 The idea, in a metaphor

Think of a consultant working remotely. They know many things, but to do their job they need to be able to:

- Read documents you send them.
- Search information online.
- Run calculations.
- Send emails.

Without these accesses, they can only give you generic advice. With these accesses, they can actually **do things**.

Tools in AI models work exactly like this: they are **external functions** the model can call when it needs to.

## 6.2 How it works, in 4 steps

```
1. You define tools, each with: name, description, parameters.
2. You include these tools in the model call.
3. The model, instead of answering immediately, can "ask": "I want to call X with these parameters".
4. You (your code) execute the call and send the result back to the model.
   It continues.
```

It's **the model that decides** whether and which tool to call. You don't force it. It reads the tool description and decides if it's useful.

## 6.3 Example in Python (Anthropic SDK)

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Returns current weather for a city. Use when the user asks about the weather, temperature or rain.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name, e.g. 'Rome' or 'New York'"
                }
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "I'm going out in Milan, do I need an umbrella?"}
    ]
)

print(response.stop_reason)   # 'tool_use'
print(response.content)       # tool_use block with name and input
```

At this point the model has **not** answered in text. It said: "I want to call `get_weather` with `city='Milan'`." It's up to you to execute the function.

```python
def get_weather(city: str) -> str:
    # actual implementation here (call to a weather API)
    return f"In {city}: 12°, light rain"

# Extract the tool call from the response
tool_use_block = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_use_block.input)

# Send the result back to the model
follow_up = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "I'm going out in Milan, do I need an umbrella?"},
        {"role": "assistant", "content": response.content},
        {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": result
        }]}
    ]
)

print(follow_up.content[0].text)
# "In Milan there's light rain, yes, take an umbrella!"
```

Same logic with OpenAI SDK, different syntax. The concepts (defining tools with schema, receiving `tool_call`, returning `tool_result`) are identical.

## 6.4 The most important thing: the description

The model picks which tool to call by reading the **description**. If the description is bad, it will pick badly.

**Bad:**
```
"description": "gets weather"
```

**Good:**
```
"description": "Returns current weather for a given city. Use it when the user asks for weather information, temperature, rain, wind, or plans activities depending on the weather."
```

**Excellent:** also add *when NOT to use it*:
```
"description": "Returns current weather for a city. Use for: temperature, rain, wind, current weather conditions.
Do not use for: long-term forecasts (beyond 24 hours), historical events, average climate data.
For ambiguous cities (e.g. 'Springfield'), ask the user for clarification first."
```

**Golden rule:** write the tool description as if explaining to a new employee who has to decide when to use it.

## 6.5 Parameter schema: precision pays

The parameter schema (JSON Schema) tells the model *how* to construct the call. Be precise:

- `type` (string, number, boolean, array, object).
- `description` for each parameter: what it represents, what format.
- `enum` if there are limited valid values.
- `required` with mandatory fields.

Rich example:

```json
{
  "name": "send_email",
  "description": "Sends a transactional email to a recipient. Use for user notifications, confirmations, password reset. DO NOT use for marketing or spam emails.",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Recipient email address, in standard format (e.g. mario@example.com)"
      },
      "subject": {
        "type": "string",
        "description": "Email subject, max 100 characters",
        "maxLength": 100
      },
      "body": {
        "type": "string",
        "description": "Email body in Markdown format. Will be converted to HTML."
      },
      "priority": {
        "type": "string",
        "enum": ["low", "normal", "high"],
        "description": "Send priority. 'high' only for password reset and critical errors."
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

The more expressive the schema, the fewer mistakes the model makes.

## 6.6 How many tools? Which ones?

**Few well-built tools > many generic tools.**

Beginner mistake: giving the agent 30 tools. The model gets confused, picks at random, does the wrong thing.

Guidelines:

- **5-15 tools** is the comfortable range for most agents.
- If more are needed, group them: instead of `read_user`, `read_order`, `read_product`, make a single `query_db(table, filters)`.
- For very different tasks, consider **specialized sub-agents** with their own tools (Ch. 4).
- Tools with **similar names** confuse the model. `search` vs `find` vs `lookup` → only one, well-defined.

## 6.7 Safe tools, dangerous tools

Tools act on the world. Typical danger categories:

| Category | Examples | Recommended policy |
|---|---|---|
| **Read-only** | `read_file`, `web_search`, `query_db` | Leave free. |
| **Reversible write** | `create_draft_email`, `add_to_cart` | Leave free but log. |
| **Non-reversible write** | `send_email`, `delete_file`, `charge_payment` | Human confirmation or whitelist. |
| **System-level** | `run_shell_command`, `exec_python` | Only in isolated sandbox. |

For dangerous tools, the typical pattern is **human-in-the-loop**: the agent proposes the action, shows what it will do, and waits for confirmation.

In Claude Code this is handled automatically: every Bash/Edit/Write asks the user for authorization, except for pre-approved permissions.

## 6.8 Tools that return a lot: truncation and pagination

A tool that returns 5MB of output saturates the context window. Best practices:

- **Truncate** outputs that are too long (e.g. only the first 2000 lines).
- **Summarize** if it makes sense (another LLM can synthesize before returning to the first).
- **Paginate** (cursor-based): the tool returns 50 results with a `next_cursor` for the next ones.
- **Filter at source**: better `query_db(filters)` returning 100 right records than `list_all()` + chat-side filtering.

The **descriptions of limits** also go in the tool: "Returns max 50 results. For more, use the `cursor` parameter."

## 6.9 Errors from tools

Tools fail. The file doesn't exist, the network drops, the API returns 500. You have to decide how to handle it:

```python
def fetch_url(url: str) -> dict:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return {"ok": True, "content": r.text[:5000]}  # truncate
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

**Always return a structured result**, even for errors. The model can read the error and retry with different parameters (e.g. correct URL). Throwing an exception "breaks" the agent.

## 6.10 MCP: the "USB-C" of tools

**Model Context Protocol (MCP)** is an open standard for serving tools to any compatible agent.

Idea: instead of re-implementing tools for each agent, write a **MCP server** that exports tools, and any client (Claude Code, Claude Desktop, Cursor) can consume them.

Examples of existing MCP servers:
- `mcp-server-filesystem` — file access
- `mcp-server-github` — issues, PRs, repos
- `mcp-server-postgres` — queries on a Postgres
- `mcp-server-slack` — messages and channels

Advantages:
- Reusability across different clients.
- Clean separation between agent and tool.
- Open ecosystem (you can publish your own server).

We'll come back to it in chapters on Claude Code (Ch. 9) and on building agents (Ch. 10).

## 6.11 Practice: design tools for a "personal assistant" agent

Exercise: imagine an agent that helps you manage your day. Which 6-8 tools would you give it?

A possible answer:

1. `read_calendar(date_range)` — reads appointments.
2. `create_event(title, start, end, attendees)` — creates an appointment.
3. `search_emails(query)` — searches in emails.
4. `compose_email(to, subject, body, send=False)` — draft/send email (with flag).
5. `list_tasks(status)` — open tasks.
6. `add_task(title, due, priority)` — adds a task.
7. `web_search(query)` — info from the web.
8. `ask_user(question)` — asks confirmation in case of ambiguity.

Note:
- Email send with `send=False` flag by default: the agent prepares, you confirm.
- `ask_user` is a tool: gives the model a *structured* way to ask questions.
- No `do_anything` tool: clear scope.

## 6.12 Key takeaways

- **Tools are what make the LLM an agent.**
- **The tool description is the most important prompt.** Explain it like to a new colleague.
- **Precise schema** of parameters = fewer model errors.
- **Few well-built tools** > many generic tools.
- **For risky tools**, human-in-the-loop or sandbox.
- **Structured errors** instead of exceptions: the model can handle them.
- **MCP** is becoming the standard for exposing tools across agents.

## 6.13 Common mistakes

- **Vague descriptions.** "Email tool" → the model doesn't know when to use it.
- **Too many similar tools.** The model picks at random.
- **Tools with hidden side effects.** "list_users" that actually also sends an email. Confuses agent and debug.
- **Tools without output limits.** They saturate context and wallet.
- **Exceptions instead of structured errors.** The model doesn't see the error, only that the loop broke.
- **Leaving dangerous tools without supervision.** "The agent dropped the prod table" isn't a joke.

---

Tools give hands and eyes. Memory gives *continuity over time*. Let's see how to manage it.

→ [Chapter 7 — Memory, context and RAG](07-memoria-contesto-e-rag.md)
