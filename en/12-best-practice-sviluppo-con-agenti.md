# 12. Best Practices for Development with Agents

This chapter is the condensation of **good habits** gathered in the previous chapters, plus some patterns that apply across the board. Think of it as a checklist to review before putting an agent in users' hands.

## 12.1 The golden rule: small, simple, observable

The single principle that summarizes everything:

> **Start small, keep it simple, make it observable.**

- **Small**: fewer tools, fewer steps, fewer tokens. Growing is easy, simplifying is hard.
- **Simple**: a linear agent with 5 well-built tools almost always beats a complex multi-agent system.
- **Observable**: without visibility into what the agent does, every bug is a mystery.

## 12.2 Recommended development workflow

### Phase 1 — Evaluation dataset (BEFORE the code)
Sounds nerdy, but it's what separates pros from amateurs.

Create a file (`evals.jsonl`) with 20-50 representative examples:

```json
{"input": "Find Anthropic's CEO", "expected_contains": ["Dario Amodei", "Anthropic"]}
{"input": "Calculate 837 * 924", "expected_contains": ["773388"]}
{"input": "Summarize section X of document Y", "expected_format": "max 3 bullets"}
```

Against this dataset you'll measure every change. We'll see more extensive evals in Ch. 14.

### Phase 2 — Minimal V1
A single agent, 3-5 tools, simple prompt. Run on the eval dataset, measure quality.

### Phase 3 — Targeted iteration
Look at the failed cases of the dataset. Look for patterns. Improve ONE change at a time:
- The prompt? Change it, re-measure.
- The tools? Add/improve descriptions, re-measure.
- The model? Try a more capable or smaller one, re-measure.

### Phase 4 — Hardening for production
- Retry, timeout, error handling.
- Iteration and budget limits.
- Logging and tracing.
- Load tests (latency with N concurrent users).
- Permissions and safety.

### Phase 5 — Gradual rollout
- Internal beta.
- Feature flag to activate with % of users.
- A/B comparison vs. baseline (e.g. manual process).
- Expansion if metrics confirm it.

## 12.3 Versioned prompts

Prompts are code. Treat them as such:

- **In git repository**, not in chat or random documents.
- **Versioned**: `prompts/v1.txt`, `v2.txt` or changelog inside.
- **Tested**: every prompt change → re-run eval suite.
- **Cited in code** as constants, not hardcoded scattered.

```python
# good
from prompts import RESEARCH_AGENT_SYSTEM
client.messages.create(system=RESEARCH_AGENT_SYSTEM, ...)

# bad
client.messages.create(system="You are an agent that...", ...)  # everywhere in codebase
```

## 12.4 Separate logic and LLM

The LLM is good at **judging**, bad at **calculating**. Guideline:

| What the LLM does | What the code does |
|---|---|
| Understand intent | Validate formats |
| Generate text | Calculate numbers |
| Classify | Make precise regex |
| Summarize | Database queries |
| Decide which tool | Execute transactions |

If you find yourself asking the LLM to do arithmetic, regex, or exact lookups — **give it a tool**, not a prompt.

## 12.5 Tool idempotency

Tools with side effects (DB writes, sending emails) should be **idempotent** or **deduplicable**.

The agent can retry. Without idempotency, retry = duplicate.

Pattern:

```python
def send_email(to: str, subject: str, body: str, idempotency_key: str = None):
    if idempotency_key and already_sent(idempotency_key):
        return {"status": "already_sent", "key": idempotency_key}
    # send
    record_sent(idempotency_key)
    return {"status": "sent", "key": idempotency_key}
```

For external APIs too, prefer those with idempotency keys (Stripe, etc.).

## 12.6 Human-in-the-loop where needed

For costly or irreversible actions:

```python
def process_refund(user_id: str, amount: float):
    if amount > 100:
        return ask_human(
            f"Refund of €{amount} to user {user_id}. Confirm? (yes/no)"
        )
    return execute_refund(user_id, amount)
```

The agent understands `ask_human` is a tool like the others, calls it, and receives the decision.

Pattern for various thresholds:

- **Read-only**: no confirmation.
- **Reversible write**: log + alert in case of anomaly.
- **Costly or irreversible write**: explicit confirmation.
- **Bulk operation**: mandatory dry-run before real execution.

## 12.7 Tests and types of tests

Common tests for an agent-based system:

### Unit tests on tools
Pure tools, no LLM. Classic tests.

### Eval tests on agent behavior
Given an input, verify the response satisfies criteria (contains keywords, correct format, does the right thing). We'll see how to write them in Ch. 14.

### Regression tests on prompts
When you change a prompt, re-run the suite. Output different from baseline → review.

### Production smoke tests
A canary running every 5 minutes with a known input. If the response is strange, alert.

### Cost tests
Maximum token limit per request. If exceeded, error. Avoids explosions in production.

## 12.8 Determinism and reproducibility

LLMs aren't deterministic. For debug and testing:

- **Temperature 0** + seed (where available) → (almost) stable output.
- **Caching of calls** during testing (e.g. VCR.py for Python): record once, then re-run offline.
- **Snapshot testing**: save a run's output and flag differences vs baseline.

Never make tests that depend on exact textual output: small variations break healthy tests. Use pattern matching, contains, structural validation.

## 12.9 Prompt security

Prompts can be attacked (Ch. 13). Main defenses:

- **Separate instructions from data**: use clear delimiters (`<doc>...</doc>`).
- **Tool whitelist**: the agent shouldn't be able to call tools not explicitly enabled.
- **Output validation**: if JSON output, validate with schema. If free output, check it doesn't contain commands (PII, SQL, code).
- **Privilege separation**: the agent talking to the external user shouldn't have the same tools as the internal one.

## 12.10 Costs under control

- **Per-request budget**: token cap.
- **Daily/monthly budget** on the provider, with alerts.
- **Adaptive model**: for simple requests, small model. For complex, large. You decide or let a router decide (small LLM that classifies difficulty).
- **Aggressive caching**: prompt caching, deterministic tool result cache, embedding cache.

Simple router example:

```python
def route_model(task: str) -> str:
    if "summarize" in task.lower() or "translate" in task.lower():
        return "claude-haiku-4-5"   # cheap
    if "design" in task.lower() or "architect" in task.lower():
        return "claude-opus-4-7"    # capable
    return "claude-sonnet-4-6"      # default
```

## 12.11 Pair programming with AI

For personal coding (with Claude Code, Cursor, etc.) there are patterns that make a difference:

### Spec first, code later
Spend the first 5-10 minutes explaining *what* you want and *why*. The agent codes better with a good brief than with ten subsequent corrections.

### Small diffs, real reviews
Let the agent make 3-4 targeted changes, then review `git diff`. Resist the temptation to "let it run for an hour" — when you come back, you have 800 lines to understand.

### Test together
Ask the agent to write the test before the implementation. Even if you're not a TDD purist, it works great in coding with AI: the test fixes the intent.

### Reject bad code
If the diff is bloated or adds unnecessary complexity, say "no, simplify, redo." Don't accept to avoid offending — the model doesn't take offense.

### Invest in context files
`CLAUDE.md`, hooks, slash commands: the investment in your workflow's "infrastructure" pays exponentially in productivity.

### "Think out loud"
For hard problems, ask it to **reason before acting**. "Explain the plan in 5 points, then proceed." Often explicit planning reveals errors in its reasoning before it executes them.

## 12.12 Avoid "cargo cult"

The field is young. Many "best practices" on Twitter are untested hypotheses. Maintain skepticism:

- **Magic phrases** ("you are a 10x engineer", "take a deep breath") usually don't help in modern models.
- **Forced chain of thought** on models that already do CoT internally → wasted tokens.
- **Multi-agent everywhere** is a fad that's being downsized: in tests, a single agent with good reflection often wins.
- **RAG by default** isn't always needed: if the dataset fits in 1M tokens and the query is one, long context is simpler.

**Test before believing.** A baseline without X, one with X, measure.

## 12.13 Documenting the agent

The agent in production is a system. It must be documented:

- **What it does** (clear scope, what it does NOT do).
- **Tools it can call** and what they do.
- **Permissions and limits** (who can use it, on what data, with what SLA).
- **Known failure modes** (what happens if X fails, where to look).
- **How it's evaluated** (link to eval dataset, reference metrics).
- **How it's modified** (where the prompts are, how to test a change).

A README next to the code, simple. When a new person arrives in the team, they thank you.

## 12.14 Key takeaways

- **Small, simple, observable.** One sentence to summarize everything.
- **Eval dataset before code.** Without it, you fly blind.
- **Prompts as code**: versioned, tested.
- **Logic/calculations to code, judgment to LLM.**
- **Tool idempotency**, **human-in-the-loop** where it costs.
- **Multiple tests**: unit, eval, regression, smoke, costs.
- **AI pair programming**: spec first, small diffs, test together.
- **Skepticism on fads**. Measure, don't believe.

## 12.15 Common mistakes

- **Launching to production without eval suite.** You'll change things without knowing if they get worse.
- **Leaving prompts scattered in the codebase.** They become impossible to audit.
- **Non-idempotent tools** + active retry = double send, double charge.
- **No `ask_user` for ambiguous cases.** The agent invents.
- **Multi-agent as default** = 3x the costs without quality gain.
- **Trusting the model without testing.** "It's fine when I try it", and then in production it does something strange.

---

Good development practices cover the "how". Now let's talk about "what can go wrong": security, costs, limits.

→ [Chapter 13 — Security, costs, limits](13-sicurezza-costi-e-limiti.md)
