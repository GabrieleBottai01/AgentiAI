# 4. Types of Agents and Architectures

The basic schema from Ch. 3 is just the start. In recent years, **architectural patterns** have emerged that fit different tasks. Knowing them lets you pick the right form instead of reinventing the wheel.

## 4.1 ReAct: thought + action

**ReAct** (Reasoning + Acting) is the simplest pattern and is what you saw in Ch. 3. At each turn the agent:

1. **Reason** — thinks about what to do, writing (even just internally) a brief reasoning.
2. **Act** — calls a tool.
3. **Observe** — receives the result.

Literal prompt pattern:

```
Question: {goal}

Thought: I need to search X
Action: web_search("X")
Observation: ...

Thought: now I compare Y and Z
Action: ...
Observation: ...

...

Final answer: ...
```

**When to use it:** linear tasks where each step depends on the previous. Search, simple debugging, q&a on documents.

**Limit:** if the task requires coordinating multiple sub-tasks, ReAct struggles because it reasons "one step at a time" without overall vision.

## 4.2 Plan-and-Execute

Variant: first the model produces a **complete plan**, then an executor (sometimes the same model, sometimes a smaller one) executes it.

```
Planner:
  1. Search articles about "X"
  2. Extract the 5 most cited
  3. Summarize each one
  4. Compare viewpoints
  5. Produce final synthesis

Executor: runs 1 → runs 2 → runs 3 → ...
```

**When to use it:**
- Tasks with many independent steps (you can parallelize).
- When the user wants to **see and approve the plan** before execution (e.g. risky actions).
- When execution is expensive and you want to avoid "discovering" mid-way that the approach was wrong.

**Limit:** if the plan is wrong, the agent executes it blindly. Often a **re-planning** mechanism is added: if a step fails, return to the planner.

## 4.3 Reflexion / Self-critique

The agent, after producing a response or action, **criticizes itself** before delivering it. Often done with a second prompt:

```
[First turn]
Proposed solution: ...

[Second turn: critique]
Review the solution above. Find errors, unconsidered cases, debatable assumptions?

[Third turn: revision]
Based on the critique, revise the solution.
```

**When to use it:** writing code, drafting important texts, quantitative analysis. Improves quality at the cost of more tokens.

**Limit:** not magic. If the model is wrong on the concept, the critique will be too.

## 4.4 Multi-agent: orchestrator + worker

A "director" agent coordinates several specialized agents. Example: a product management agent that delegates to a backend agent, a frontend one, a QA one.

```
                ┌─────────────────┐
                │   ORCHESTRATOR  │
                │ (decides who)   │
                └────────┬────────┘
            ┌───────────┼───────────┐
            ▼           ▼           ▼
       ┌────────┐  ┌────────┐  ┌────────┐
       │  Web   │  │ Coder  │  │ Writer │
       │researcher│ │       │  │        │
       └────────┘  └────────┘  └────────┘
```

**When to use it:**
- Highly heterogeneous tasks where different "skills" are needed.
- When you want a **specialized system prompt** for each role (a coder is more effective with a coder prompt).
- When you want to parallelize independent work.

**Limit:** coordination complexity. More agents = more tokens = more time = more failure points.

In Claude Code, for example, the main agent can launch **subagents** for delegated tasks (Explore, Plan, etc.). It's the orchestrator-worker pattern applied to coding.

## 4.5 Multi-agent: debate / consensus

Multiple agents propose independent solutions, then compare. Useful when uncertainty is high and you want more "viewpoints":

```
Agent A proposes: "Let's use PostgreSQL"
Agent B proposes: "Let's use MongoDB"
Agent C (judge): "A is right because the data is relational..."
```

**When to use it:** design decisions, critical analyses, evaluations where multiple perspectives help.

**Limit:** "consensus" often converges on mediocre answers (AI tends to accommodate). It works better if the roles are *really* different.

## 4.6 Swarm / market-based

Many smaller agents, each with a sub-goal, competing or collaborating in a decentralized way. Fascinating pattern in research, rare in production because it's hard to debug.

## 4.7 Tool-using agent vs. Code-generating agent

An important practical distinction.

- **Tool-using agent**: the agent calls predefined tools. You have fine control over available tools, simple audit. Example: a customer support agent that uses `search_kb()`, `create_ticket()`, `send_email()`.

- **Code-generating agent**: the agent *writes code* (usually Python) and runs it in a sandbox. Extremely flexible — anything Python can do, the agent can do. Extremely dangerous if not properly sandboxed.

Well-known examples of the second type: ChatGPT with Code Interpreter, Claude with the `code_execution` tool, Open Interpreter.

**Tradeoff:**
- Tool-using = safe, predictable, limited.
- Code-generating = flexible, powerful, risky.

For many real-world cases, code-generating solves in 1 step what a tool-using solves in 10. But you only want it running in isolated environments.

## 4.8 Ambient agent / always-on

Agents that run in the background, monitoring events and acting only when needed. Examples:

- An agent that watches your email inbox and automatically archives/labels.
- An agent that monitors production logs and opens a ticket when it spots an anomaly.
- An agent that observes a Git repo and proposes refactors.

Technically they are agents that get "woken up" by a trigger (cron, webhook, event) and then follow the normal loop.

**When to use them:** monitoring, automation of repetitive workflows.

**Caution:** since they act when you're not present, **authorizations** must be defined with great care. An always-on agent that can write to Slack or delete files needs human review on critical steps.

## 4.9 Quick comparison: which pattern do I pick?

| Case | Recommended pattern |
|---|---|
| Q&A with multi-step search | ReAct |
| Task with long plan, you want visibility | Plan-and-Execute |
| Important code or text, you want quality | ReAct + Reflexion |
| Highly heterogeneous tasks | Orchestrator + worker |
| Difficult design decision | Multi-agent debate |
| Arbitrary data calculations/transformations | Code-generating agent |
| Background monitoring | Ambient agent (event-driven) |

They're not mutually exclusive: a real system often combines two or three.

## 4.10 Practice: identify the architecture

Open these products and try to recognize the pattern (it's a mental exercise, there's no single right answer):

- **ChatGPT with "Deep Research"**: produces a plan, then browses the web for hours, then synthesizes. → Plan-and-Execute, code-generating on results.
- **Claude Code**: main agent with subagents for exploration/planning. → Orchestrator + worker, ReAct.
- **Cursor / Aider**: autocomplete + code edit in real time. → More tool than "real" agent (little loop).
- **Devin**: autonomous coding agent. → Plan-and-Execute, code-generating.
- **Zapier AI**: scripted workflow that calls LLMs in some steps. → Automation with AI, not agent.

## 4.11 Key takeaways

- **ReAct** is the starting pattern, simple and powerful.
- **Plan-and-Execute** when you want plan visibility or parallelization.
- **Reflexion** when quality matters more than speed.
- **Multi-agent** when tasks are heterogeneous or you want role specialization.
- **Code-generating** is maximum flexibility but requires serious sandboxes.
- **Ambient agent** = agent triggered by events instead of prompts.
- **Combining patterns is normal and often better than picking just one.**

## 4.12 Common mistakes

- **Starting multi-agent before single.** Almost always a single well-built agent is enough. Multi-agent is a conscious choice, not a default.
- **Plan-and-Execute with overly detailed plans.** If the plan has 30 steps, you're back in ReAct. Keep plans of 3-7 steps.
- **Infinite Reflexion.** "Critique and revise" can loop. Force *one* round of critique only.
- **Ignoring the "ambient" pattern** when actually only standard automation is needed. Not everything must have a loop.

---

We've covered the architectural fundamentals. Now let's move on to **practical techniques** for getting the most out of agents, starting with the most important: prompt engineering.

→ [Chapter 5 — Prompt engineering](05-prompt-engineering.md)
