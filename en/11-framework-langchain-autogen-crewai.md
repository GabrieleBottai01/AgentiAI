# 11. Frameworks: LangChain, AutoGen, CrewAI

Frameworks provide **high-level abstractions** for building agents without writing the loop by hand. They give you: unified model calls, ready-made tools, memory, multi-agent, observability.

Classic tradeoff: **development speed vs. control**. Good to know when to choose which, and when *not* to use a framework.

## 11.1 Overview

| Framework | Focus | Strengths | When to use |
|---|---|---|---|
| **LangChain** | Composing chains and agents | Huge ecosystem, integrations with everything | RAG pipelines, fast prototypes, devs who want ready-made tools |
| **LangGraph** | Workflow as graph | Fine control, explicit state, debug | Complex agents requiring branching, retry, human-in-the-loop |
| **AutoGen** | Conversational multi-agent | "Agents talking to each other" pattern | Simulations, debate, problems benefiting from multiple roles |
| **CrewAI** | Multi-agent oriented to "teams" | "Role + task + tool" abstraction | Business-like workflows (research → write → edit) |
| **LiteLLM** | Unified adapter for LLMs | Uniforms API across OpenAI, Anthropic, local, etc. | When you want provider-agnostic |
| **Pydantic AI** | Type-safe agents in Python | Type rigor, structured validation | Python backend that values type safety |
| **Vercel AI SDK** | Agents in TypeScript for web apps | Streaming UI, React hooks | Frontend/full-stack JS |

They are not mutually exclusive. A typical stack might be: `LiteLLM` (provider-agnostic) + `LangGraph` (orchestration) + `pgvector` (memory) + `Langfuse` (observability).

## 11.2 LangChain: state of the art (with caveats)

LangChain is the most popular framework. It's had a turbulent evolution: the first version ("classic chains") was superseded by one based on **LCEL (LangChain Expression Language)** and then accompanied by **LangGraph** for agents.

### Example: RAG chain with LangChain

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Vector store already populated
vstore = Chroma(persist_directory="./db", embedding_function=OpenAIEmbeddings())
retriever = vstore.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_template("""
Reply using only the provided context.

Context: {context}

Question: {question}
""")

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | ChatAnthropic(model="claude-opus-4-7")
)

print(chain.invoke("What's the travel reimbursement policy?"))
```

**Pros:**
- 5 lines for working RAG.
- Change models by changing 1 import.
- Ecosystem with hundreds of integrations (DBs, APIs, vector stores, parsers).

**Cons:**
- Unstable API (frequent breaking changes).
- "Magic" that hides problems: when something goes wrong, debug is a journey.
- Sometimes forced abstractions (LCEL can become hard to read).

**Verdict:** great for **prototypes** and to use integrations you don't want to reimplement. For production agents, prefer **LangGraph** (below).

## 11.3 LangGraph: workflow as graph

LangGraph is LangChain's "grown-up" sibling. The agent is modeled as a **graph of nodes** where each node is a function and edges are conditional transitions.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    iterations: int

def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response], "iterations": state["iterations"] + 1}

def call_tools(state: AgentState):
    last = state["messages"][-1]
    results = [execute_tool(call) for call in last.tool_calls]
    return {"messages": results}

def should_continue(state: AgentState):
    if state["iterations"] >= 10:
        return END
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tools)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()
result = app.invoke({"messages": [...], "iterations": 0})
```

**Pros:**
- Explicit state → easy debug and replay.
- Conditional branching, loops, native human-in-the-loop.
- State persistence between runs (checkpointing).
- Production-ready.

**Cons:**
- Steeper learning curve.
- Overkill for simple tasks.

**When to use it:** complex agent with multiple branches, retry, human approvals, workflow replay.

## 11.4 AutoGen: agents talking to each other

AutoGen (Microsoft Research) focuses on **conversational multi-agent**: define agents with roles, let them dialogue, let the solution emerge.

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="coder",
    llm_config={"config_list": [{"model": "gpt-5", "api_key": "..."}]},
    system_message="You are an expert Python programmer."
)

reviewer = AssistantAgent(
    name="reviewer",
    llm_config={...},
    system_message="You are a rigorous code reviewer."
)

user = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "./tmp"}
)

user.initiate_chat(
    assistant,
    message="Write a function that calculates Fibonacci with memoization"
)
# then reviewer comments, coder revises, user runs, etc.
```

**Pros:**
- Natural pattern for problems benefiting from "multiple viewpoints".
- Free multi-agent conversation handling.
- Great for simulations and debate.

**Cons:**
- Agents chatting = many tokens. High cost.
- Converging to a "good" answer requires fine system prompt tuning.
- Often a single agent with reflection does the same at 1/3 the cost.

**When to use it:** educational simulations, dialog generation, team problems where roles are *truly* distinct.

## 11.5 CrewAI: task-driven agent teams

CrewAI uses the "company team" metaphor: define **agents** (roles), **tasks** (things to do), **tools** (instruments), and compose them in a **crew**.

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Senior Researcher",
    goal="Find accurate information on topic X",
    backstory="You are a meticulous researcher with years of experience...",
    tools=[web_search_tool, scrape_tool]
)

writer = Agent(
    role="Tech Writer",
    goal="Write clear articles based on solid research",
    backstory="...",
    tools=[]
)

research_task = Task(
    description="Investigate recent developments in {topic}",
    expected_output="Bulleted list with 5-7 key facts and sources",
    agent=researcher
)

write_task = Task(
    description="Write a popular article based on the research findings",
    expected_output="800-word article, clear tone",
    agent=writer,
    context=[research_task]   # passes research output as context
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

result = crew.kickoff(inputs={"topic": "AI agents in 2026"})
```

**Pros:**
- Easy mental abstraction for those not from ML.
- Good for linear workflows (research → write → review).
- Active community, many templates.

**Cons:**
- Magic that sometimes produces mediocre results.
- Personality prompts ("backstory") can become novelistic and waste tokens.
- For short tasks, a single agent is more efficient.

**When to use it:** automation of business workflows with clear steps, prototype of an "AI team" to show non-programmers.

## 11.6 LiteLLM: the universal adapter

Not an agent framework, but a **unified wrapper** for all providers. Same API, different models:

```python
from litellm import completion

# Change only "model"
r1 = completion(model="claude-opus-4-7", messages=[...])
r2 = completion(model="gpt-5", messages=[...])
r3 = completion(model="gemini/gemini-2-pro", messages=[...])
r4 = completion(model="ollama/llama4", messages=[...])  # local!
```

It gives you:
- Easy provider switching.
- Fallback routing (if Anthropic is down, try OpenAI).
- Telemetry and cost tracking.
- Proxy server to centralize calls from multiple services.

**When to use it:** whenever you expect to try multiple providers or want to reduce vendor lock-in.

## 11.7 Pydantic AI: type-safe agents

From Pydantic (most loved Python validation library). Approach: **define I/O with Python types**, the framework handles serialization/parsing.

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    temperature_celsius: float
    conditions: str

agent = Agent(
    "claude-opus-4-7",
    result_type=WeatherResponse,
    system_prompt="You are a weather agent."
)

result = agent.run_sync("What's the weather in Rome?")
print(result.data.city)               # str
print(result.data.temperature_celsius) # float
```

**Pros:**
- Automatic output validation.
- Excellent developer experience in Python (autocomplete, mypy).
- Lightweight, zero magic.

**Cons:**
- Younger than LangChain, fewer integrations.
- Less developed multi-agent.

**When to use it:** Python backend where type rigor matters (FastAPI, microservices).

## 11.8 Vercel AI SDK: agents in TypeScript

For web apps (Next.js, Svelte, etc.), the Vercel AI SDK is effectively the standard.

```ts
import { streamText, tool } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const result = await streamText({
  model: anthropic('claude-opus-4-7'),
  tools: {
    weather: tool({
      description: 'Get weather for a city',
      parameters: z.object({ city: z.string() }),
      execute: async ({ city }) => fetchWeather(city),
    }),
  },
  prompt: 'What is the weather in Rome?',
});
```

It gives you streaming, tools, structured output, React hooks (`useChat`, `useCompletion`). For chat UI in web apps, it's the fastest way.

## 11.9 When NOT to use a framework

Frameworks have a cost: **hidden complexity + dependencies + lock-in**.

Consider going without if:

- Your agent is simple (1-2 tools, direct loop). 100 lines of Python with pure SDK are clearer than 30 lines of LangChain.
- You're in a context with strict dependency constraints (embedded, minimal packages).
- You have to debug subtle behavior and the framework's magic makes everything opaque.
- Your company has security policies preventing unverified npm/pip dependencies.

**Pragmatic rule:** start with pure SDK. When you find yourself writing the same boilerplate for the third time (RAG, retry, multi-agent), it's time to consider a framework.

## 11.10 Quick comparison: choosing

```
Have a simple workflow? → Pure SDK (Ch. 10).
Want quick RAG? → LangChain.
Complex agent, branching, human-in-the-loop? → LangGraph.
Conversational multi-agent? → AutoGen.
"Team-style" business workflow? → CrewAI.
Type-safe Python backend? → Pydantic AI.
TS/JS web app? → Vercel AI SDK.
Want to switch providers? → LiteLLM everywhere.
Observability? → Langfuse or LangSmith (orthogonal to all).
```

## 11.11 Observability: the piece you can't skip

Once in production, agents break in unpredictable ways. Without structured tracing, you're blind.

Tools that integrate the frameworks above:

- **Langfuse** (open-source, self-hostable). Traces chains, agents, costs, errors.
- **LangSmith** (from LangChain Inc, hosted). Commercial equivalent, perfect integration with LangChain/LangGraph.
- **Helicone** (proxy + observability). Slips between you and the API.

They let you:
- See every call with prompt, output, tokens used, latency.
- Replay problematic sessions.
- A/B test on prompts.
- Alert on errors or anomalous costs.

Spending 1 hour to set up observability at the start saves days of debugging later.

## 11.12 Practice: redo the agent from Ch. 10 in LangGraph

Exercise: take the research agent from Ch. 10 and rewrite it in LangGraph. You'll see:
- How much "loop" code disappears.
- How much you gain in observability (trace every step).
- How much you lose in simplicity.

Compare the two and decide which convinces you more *for your use*.

## 11.13 Key takeaways

- **Start with pure SDK.** Understand how it really works.
- **LangChain** for prototypes and RAG, **LangGraph** for production agents.
- **AutoGen / CrewAI** for multi-agent, but evaluate if it's really needed.
- **LiteLLM** everywhere for provider-switching.
- **Vercel AI SDK** for TS web apps.
- **Observability** (Langfuse or similar) is not optional.

## 11.14 Common mistakes

- **Skipping pure SDK.** Without understanding the fundamentals, frameworks become magic black boxes.
- **Adopting unstable frameworks in production.** LangChain has breaking changes every 6 months.
- **Multi-agent because "it's cool".** An agent with reflection often beats a team of chatty agents.
- **No observability.** "Works locally" → in production explodes without you understanding why.
- **Not pinning dependency versions.** Automatic update = unpleasant surprises.

---

You know how to build and orchestrate agents. Now let's talk about **how to work well with them**: practices, workflows, work quality.

→ [Chapter 12 — Best practices for development with agents](12-best-practice-sviluppo-con-agenti.md)
