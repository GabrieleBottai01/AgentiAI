# 3. Anatomy of an Agent

We know what an agent is (Ch. 1) and how its engine works (Ch. 2). Now let's open the hood: what pieces an agent is made of, and how they combine.

## 3.1 The mental model

Keep this diagram in mind. It's literally the entire chapter in one drawing.

```
                ┌──────────────────────────────────────┐
                │            AGENT LOOP                │
                │                                      │
   goal ──────▶│   1. PERCEIVE   (what happened)      │
                │           │                          │
                │           ▼                          │
                │   2. REASON     (what to do now)     │  ◀── LLM
                │           │                          │
                │           ▼                          │
                │   3. ACT        (call a tool)        │  ◀── Tool
                │           │                          │
                │           ▼                          │
                │   4. OBSERVE    (what changed)       │
                │           │                          │
                │           └──── back to 1 ───────────┤
                │                                      │
                │   5. STOP    (goal reached?)         │
                └──────────────────────────────────────┘
                              │
                              ▼
                       final response
```

**The loop is the heart of everything.** Everything else is details about how to implement each step.

## 3.2 The four fundamental components

### a. The model (brain)
It's the LLM. Receives as input the current state (everything that has happened so far) and produces an output: a final response, or a tool call request.

### b. The tools (hands and eyes)
Functions the agent can call to **act** (write files, make HTTP requests) or **perceive** (read files, search the web). Without tools, the agent is blind and immobile — it can only talk.

Typical tool examples:
- `read_file(path)` — read a file
- `web_search(query)` — search the web
- `run_python(code)` — execute Python code
- `send_email(to, subject, body)` — send an email
- `query_database(sql)` — query a DB

Tools are declared with a **schema** (usually JSON Schema) describing name, parameters, and description. The model reads the schema and decides when and how to call them (Ch. 6).

### c. Memory (notebook)
The agent needs to remember what it has done. There are different levels:

- **Short-term memory** = the context window. The whole ongoing conversation is sent back to the model each step. It's the "working" memory.
- **Long-term memory** = information saved outside the context (files, databases, vector stores) and recalled when needed. It lets the agent "remember" things between different sessions (e.g. user preferences, project facts).
- **Episodic memory** = log of past actions. Useful for debugging and to avoid redoing the same things.

We'll cover memory and RAG in detail in Ch. 7.

### d. The orchestrator (director)
The piece of code that holds it all together: takes the model's output, executes the requested tools, collects results, sends them back to the model, checks the stop condition. It's what you write (or use a framework — Ch. 11).

## 3.3 Step-by-step example: an agent that searches information

Let's see the loop in action. Goal: **"Find who Anthropic's CEO is and when the company was founded."**

**Turn 1**

```
State: user message "Find who Anthropic's CEO is and when the company was founded"

LLM thinks: "I need to search."
LLM produces: tool_call("web_search", query="CEO Anthropic founding year")

Orchestrator: executes web_search → receives results (page snippets)
```

**Turn 2**

```
State: all of turn 1 + search result

LLM thinks: "I have partial info, I need to open a reliable link."
LLM produces: tool_call("fetch_url", url="https://www.anthropic.com/company")

Orchestrator: executes fetch_url → receives HTML
```

**Turn 3**

```
State: all previous turns + page content

LLM thinks: "I have the info I need."
LLM produces: final response "Anthropic's CEO is Dario Amodei. The company was founded in 2021."

Orchestrator: no tools to execute → STOP, returns the response.
```

Three LLM turns, two tool calls, one response. **That's an agent.**

## 3.4 The agent's "state": what it contains

At each turn, the model receives as input a state that grows. Typically:

```python
state = [
    {"role": "system", "content": "You are a research agent..."},
    {"role": "user", "content": "Find Anthropic's CEO"},
    {"role": "assistant", "tool_calls": [{"name": "web_search", ...}]},
    {"role": "tool", "content": "Results: ..."},
    {"role": "assistant", "tool_calls": [{"name": "fetch_url", ...}]},
    {"role": "tool", "content": "<html>..."},
    {"role": "assistant", "content": "The CEO is Dario Amodei..."},
]
```

Notice two things:

1. **The state is the complete history.** Every turn the model re-sees everything.
2. **It grows fast.** 10 turns with tools returning HTML can saturate the context window. Context management is a crucial skill (Ch. 7).

## 3.5 The stop condition

When does the agent stop? Four typical cases:

1. **Natural stop**: the model no longer calls tools and produces a final response.
2. **Iteration limit**: the orchestrator stops the agent after N turns (e.g. 25). Lifesaver against infinite loops.
3. **Budget limit**: the agent has consumed too many tokens / money → stop.
4. **Explicit user stop**: in CLIs like Claude Code, an `Esc` interrupts.

**Important**: without an iteration limit, an agent can loop forever (e.g. keeps calling the same tool because it misinterprets an error). Always set one.

## 3.6 Planning: think before acting

More sophisticated agents separate two phases:

- **Planning**: the model produces a plan in natural language ("To answer I'll do these steps: 1. search X, 2. analyze Y, 3. compare").
- **Execution**: the agent executes the plan one step at a time, with tools.

Advantages of explicit planning:
- The user can **review the plan** before letting the agent act (useful for risky actions).
- The agent is less prone to wandering.
- Independent steps execution can be parallelized.

Disadvantages:
- Slower (one extra LLM step).
- If the plan is wrong, the agent executes useless things.

We'll see the "Plan-and-Execute" architecture in Ch. 4.

## 3.7 Practice: a minimal loop in Python (pseudo-code)

To fix the idea, here's the skeleton of an agent in pseudo-Python. It's not yet runnable code (we'll see that in Ch. 10), but it reads like prose.

```python
def agent_loop(goal: str, tools: dict, max_iterations: int = 25):
    history = [
        {"role": "system", "content": "You are an agent. Use tools when needed."},
        {"role": "user", "content": goal},
    ]

    for step in range(max_iterations):
        # 1. Call the model with all the state
        response = llm.chat(messages=history, tools=list(tools.values()))

        # 2. Update the history with the model's response
        history.append(response.message)

        # 3. If there are no tools to call, we're done
        if not response.tool_calls:
            return response.content

        # 4. Execute the requested tools
        for call in response.tool_calls:
            result = tools[call.name](**call.arguments)
            history.append({"role": "tool", "content": result, "tool_call_id": call.id})

    return "Iteration limit reached."
```

This really is 90% of what you need to know to build an agent from scratch. The rest is improving tools, handling errors, adding memory.

## 3.8 Key takeaways

- **Loop = soul of the agent.** Perceive → reason → act → observe → repeat.
- **Four components**: model, tools, memory, orchestrator.
- **State is the history.** The whole dialogue is sent back to the model at every turn.
- **Always set an iteration limit.** Avoids infinite loops.
- **Explicit planning** is useful for complex tasks and for transparency with the user.

## 3.9 Common mistakes

- **Loop without limit.** The agent enters a spiral, burns €10 of tokens in 5 minutes.
- **Tools without descriptions.** If you don't explain to the model *when* to use a tool, it picks at random.
- **Tools that return too much.** A tool returning 10MB of HTML saturates the context. Truncate, summarize, paginate.
- **Mixing logic and LLM.** Anything deterministic (validations, precise calculations) keep in code; leave to the LLM only what requires judgment.
- **Changing behavior only via system prompt.** Sometimes a well-designed tool is more effective than three paragraphs of instructions.

---

Now that you know what an agent looks like, let's see the **different forms** it can take: ReAct, Plan-and-Execute, multi-agent. Each solves different problems.

→ [Chapter 4 — Types of agents and architectures](04-tipi-di-agenti-e-architetture.md)
