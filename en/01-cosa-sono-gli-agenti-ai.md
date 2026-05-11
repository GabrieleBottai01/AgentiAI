# 1. What AI Agents Are

> "An AI agent is a program that uses an LLM to decide what to do, act, see the result and start again."

That's all there is to it. The rest of the chapter exists to show why this simple sentence changes everything.

## 1.1 From chatbot to agent: a story in three steps

### Step 1 — The chatbot (2022)
You write a question, the model answers. End.

```
You:    "What's the capital of France?"
Bot:    "Paris."
```

The bot **doesn't act**. It doesn't open browsers, read files, or write to your disk. It's a conversational machine: text in, text out.

### Step 2 — The assistant with tools (2023)
We give the model the ability to **call functions**. Now if you ask for the weather, it can actually go look it up.

```
You:    "What's the weather in Rome?"
Bot:    [calls get_weather("Rome")]
        [receives "18°, clear"]
        "It's 18 degrees and clear in Rome."
```

More useful, but still reactive. You ask one thing, it does one thing.

### Step 3 — The agent (2024 onward)
Now let's give it a goal, not a command. And let's let it work in a **loop**: think, act, observe the result, rethink, re-act. Until it's done.

```
You:    "Find the 5 best-rated Japanese restaurants in Milan,
         book the one available Saturday night for 4 people."
Agent:  [searches Google]
        [reads reviews]
        [compares results]
        [calls booking API]
        [checks Saturday availability]
        [if first is full, tries the second]
        [confirms]
        "Booked Sushi B for Saturday the 20th at 9pm."
```

This is an agent: **an LLM in a loop, with tools and a goal**.

## 1.2 The useful definition

Let's agree on an operational definition. An **AI agent** is a software system with four ingredients:

1. **A model** (LLM) that reasons and decides.
2. **Tools** that the model can call to act on the world: read files, make HTTP requests, run code, query databases.
3. **A loop** that repeats: the model produces an action → the system executes it → the result returns to the model → the model decides the next action.
4. **A stop criterion**: the agent halts when it reaches the goal, exhausts its attempts, or the user interrupts it.

Without the loop and tools, you have a chatbot. With them, you have an agent.

## 1.3 What makes them powerful (and why now)

Three factors have come together over the last few years:

- **Models can follow complex instructions.** GPT-3.5 was already good at chatting; modern models (Claude 4, GPT-5, Gemini 2) can *plan* and *course-correct* mid-task.
- **"Tool use" has become standard.** All the major APIs offer a structured mechanism to declare tools and have the model call them (we'll see this in Ch. 6).
- **Context windows have grown.** Models with 200K-1M token contexts can "keep in mind" entire codebases, books, or long conversations.

Result: for many tasks that until recently required a human expert plus custom scripts, today a well-configured agent is enough.

## 1.4 What an AI agent is NOT

To avoid confusion, a few important distinctions.

| Not an agent | What it is instead |
|---|---|
| A chatbot (even a good one) | A conversational interface without an autonomous loop. |
| A single complex prompt | A *single generation*. No action, no feedback. |
| A scripted pipeline where AI does one step | A traditional workflow that uses AI as a function. |
| Classic RPA (Robotic Process Automation) | Rule-based automation, not decision-based. |

The line is blurry. **The key question is: does the system decide on its own what to do at the next step?** If yes, it's an agent. If the next action is already written in the code, it's automation.

## 1.5 When an agent makes sense (and when not)

AI agents are powerful, but not free: they cost tokens, are slower than a direct call, and introduce uncertainty (the same input can lead to slightly different behaviors).

**Good use cases:**
- **Heterogeneous** tasks where the steps aren't known in advance (research, analysis, debugging).
- Work that requires **judgment** (summarizing, classifying, drafting).
- Interactions with **many sources** (searching across systems, aggregating).
- **Exploration** in complex environments (a codebase, a dataset).

**Bad use cases:**
- Deterministic computations (1+1 is better done by Python).
- High-frequency operations where every millisecond counts.
- Regulatory/financial logic where rigorous audit trail is needed.
- Tasks where one mistake costs a lot and isn't recoverable (irreversible deletes without supervision).

A good rule: **if you can write a script in 30 minutes, don't use an agent.** If you don't even know where to start, an agent is the right solution.

## 1.6 Practice: spot an agent in 30 seconds

Open these three products (even just their demo pages) and try to classify them:

1. **An email-writing assistant** that waits for you to tell it what to write → **chatbot**.
2. **A code copilot** that, given a bug report, explores the code, proposes a fix, writes tests and opens the PR → **agent**.
3. **A Slack integration** that automatically translates messages to English when one comes in in Italian → **automation with AI**, but not a true agent (one step, no loop).

The exercise becomes intuitive after 4-5 examples. You'll come back to this distinction many times.

## 1.7 Key takeaways

- **An AI agent = LLM + tools + loop + goal.** Without the loop, it's a chatbot.
- **The agent's value lies in autonomous decision-making**: it decides what to do at the next step.
- **More freedom = more power, but also more risk.** An agent that errs autonomously can do damage a chatbot can't.
- **They're not suitable for everything.** For deterministic tasks, writing traditional code is better.
- **The word "agent" is overused.** When a product calls itself "agentic," ask yourself: is there a loop? Are there tools? Does it decide on its own?

## 1.8 Common mistakes

- **Confusing "AI" with "agent".** Gmail uses AI for smart replies, but that's not an agent.
- **Thinking an agent is "smart" like a human.** It isn't. It's good at following patterns and using tools, but it has no common sense or lived experience.
- **Giving the agent too vague a goal.** "Improve my business" doesn't work. "Analyze sales.csv and find the 3 products with the largest drop in Q1" works.
- **Letting the agent run without supervision on irreversible actions.** Deletes, payments, customer emails: human confirmation is needed, at least at first.

---

Next chapter: we'll understand the **engine** that makes all this work, the LLM. Without diving into math, but understanding *enough* to use them well.

→ [Chapter 2 — How LLMs Work](02-come-funzionano-gli-llm.md)
