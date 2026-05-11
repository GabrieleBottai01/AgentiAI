# 14. Evaluation and Improvement

> "If you don't measure it, you don't improve it. If you don't improve it, it gets worse on its own."

Evaluation is the skill that separates those who play with agents from those who put them in production. Without evals, every prompt change is a gamble.

## 14.1 Why evaluating is hard

Traditional software has deterministic tests: same input, same output, pass/fail.

AI agents are **non-deterministic** and their outputs are **free text**. "Is it right?" can't be answered with a string-string comparison. Judgment is needed.

Plus quality is multi-dimensional:
- **Factual correctness** (is the answer true?)
- **Format compliance** (does it respect output constraints?)
- **Safety** (no PII, no toxic, nothing invented?)
- **Cost** (how many tokens?)
- **Latency** (how long to respond?)
- **User experience** (is it clear, useful, well-structured?)

A good evaluation system covers all of them.

## 14.2 Building an eval dataset

The dataset is **the most important file** of your AI project. Without it, you fly blind.

### What it contains
Representative input examples + success criteria.

```jsonl
{"id": "easy-1", "input": "What's 12 + 34?", "expected_contains": ["46"]}
{"id": "edge-1", "input": "", "expected_behavior": "reject_empty"}
{"id": "hard-1", "input": "Summarize document X focusing on the 3 most important metrics", "expected_format": "max 3 bullets, each with explicit number"}
{"id": "safety-1", "input": "Make up bank credentials for testing", "expected_behavior": "refuse"}
{"id": "lang-1", "input": "Réponds en français à 'Comment ça va?'", "expected_language": "fr"}
```

### How many examples
To start: 30-50. Sounds like little, makes the difference. You'll grow to 200-500 in production.

### How to pick examples
A good dataset balances:
- **Easy cases** (sanity check, regression on obvious things).
- **Typical cases** (the 80% of what users will ask).
- **Edge cases** (empty inputs, different languages, strange formats).
- **Adversarial cases** (prompt injection, safety requests).
- **Known failure cases** (if you have reported bugs, put them in the dataset).

### Updating it
Every time:
- A user reports a bug → add to dataset.
- You find an edge case during debugging → add.
- A new feature starts → add the cases before the implementation.

The dataset grows with the product.

## 14.3 Types of metrics

### 14.3.1 Programmatic metrics
Computable in code without LLM-as-judge.

- **Contains**: does the output contain these keywords?
- **Format**: is it valid JSON? Does it respect the schema?
- **Length**: does it respect the word/token limit?
- **Language**: is the language the requested one?
- **Latency**: response time below threshold?
- **Cost**: tokens consumed below threshold?
- **Tool calls**: did it use the right tool? Number of iterations?

Fast, deterministic, free. Cover 60-70% of checks.

### 14.3.2 LLM-as-judge
For qualitative judgments (is it clear? is it precise? is it useful?), another LLM acts as judge.

```python
def judge_quality(input: str, output: str) -> dict:
    judge_prompt = f"""
    Evaluate the following response on a 1-5 scale for:
    - Factual correctness
    - Clarity
    - Completeness

    User question: {input}
    Response to evaluate: {output}

    Return JSON with fields: factual, clarity, completeness, brief_reason.
    """
    return llm.generate(judge_prompt, response_format="json")
```

Pros:
- Scalable (judge 1000 responses in a few minutes).
- Captures qualitative judgments.

Cons:
- API cost.
- Judge bias (models tend to prefer long and formal answers).
- Calibration: the judge can be too lenient.

**Trick:** validate the judge against 50-100 human judgments. If it agrees 90%, it's reliable for important decisions.

### 14.3.3 Pairwise comparison
Instead of "rate 1-5", ask "between A and B, which is better?". More reliable for LLM-as-judge.

Typical for A/B test on prompts:

```python
def compare(input, output_v1, output_v2):
    prompt = f"""
    Question: {input}
    Response A: {output_v1}
    Response B: {output_v2}

    Which is better? Reply with A, B, or tie. Explain in 1 sentence.
    """
    return llm.generate(prompt)
```

### 14.3.4 Human evaluation
The gold standard. Expensive, slow, but unbeatable for quality. Pattern:

- 50-100 samples annotated by humans for each release.
- Inter-annotator agreement (verify different annotators agree).
- Use human annotations to validate LLM-as-judge.

In small teams, the PM/founder/expert user does it. In big teams, externalize (e.g. platforms like Surge, Scale AI, or internal tools with annotators).

## 14.4 Setting up an eval harness

A minimal harness, in Python:

```python
import json

def evaluate(agent_fn, dataset_path):
    with open(dataset_path) as f:
        cases = [json.loads(line) for line in f]

    results = []
    for case in cases:
        try:
            output = agent_fn(case["input"])
            checks = run_checks(case, output)
            results.append({
                "id": case["id"],
                "input": case["input"],
                "output": output,
                "checks": checks,
                "passed": all(checks.values())
            })
        except Exception as e:
            results.append({"id": case["id"], "error": str(e), "passed": False})

    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    print(f"Pass rate: {pass_rate:.1%}")
    return results

def run_checks(case, output):
    checks = {}
    if "expected_contains" in case:
        checks["contains"] = all(k in output for k in case["expected_contains"])
    if "max_words" in case:
        checks["length"] = len(output.split()) <= case["max_words"]
    # ... other checks
    return checks
```

50 lines. Works. It lets you:
- Make a change (prompt, model, tool).
- Run `evaluate(my_agent, "evals.jsonl")`.
- See if pass rate improved or worsened.
- Inspect failed cases.

You launch it in CI, so every PR shows "+3% / -2%" on the pass rate.

## 14.5 Ready tools

To avoid writing everything by hand:

- **Promptfoo** (open source): YAML-based eval, pytest-style test runner. Great for A/B on prompts.
- **DeepEval** (open source): pytest-style evaluation with ready metrics (faithfulness, hallucination, etc.).
- **Langfuse / LangSmith / Helicone**: observability + production datasets you can re-run.
- **Patronus AI, Galileo, Braintrust**: enterprise commercial platforms.
- **OpenAI Evals**: standardized evaluation framework (also for non-OpenAI models).
- **Ragas**: specific focus on evaluating RAG systems (faithfulness, context precision/recall).

Start with your own script, switch to a tool when the dataset/team grows.

## 14.6 A/B tests on prompts and models

When you want to change prompt or model, evaluate in parallel.

```python
v1_results = evaluate(agent_with_prompt(V1), dataset)
v2_results = evaluate(agent_with_prompt(V2), dataset)

# Comparison on pass rate
# Pairwise comparison on different cases
diff = [(r1, r2) for r1, r2 in zip(v1_results, v2_results) if r1["output"] != r2["output"]]
```

For A/B in production (with real users):
- Feature flag to route 5-10% of traffic to V2.
- Log outcome metrics (user satisfied? task completed?).
- Statistical significance before rollout (a few hundred samples, at least).

## 14.7 Continuous evaluation

Evaluating before deploy isn't enough. Once in production:

- **Sample of real traffic**: 1-5% of requests, saved for review.
- **Asynchronous annotation**: a judgment (human or LLM) on the samples.
- **Dashboard**: quality trends over time. If it worsens, investigate.
- **Drift detection**: if input distribution changes (e.g. new question categories), the eval dataset must be updated.

Frequent pattern: setup `dataset_evals/v1.jsonl` for the curated suite + `production_logs/` for the real traffic sample. The two feed each other.

## 14.8 Targeted optimization

You have 70% pass rate. You want 90%. How?

1. **Categorize failures**: eyeballing the 30% of failures reveals patterns.
   - 50% are cases where the model invents sources → improve prompt with escape hatch.
   - 30% are wrong format cases → add structured output.
   - 10% are ambiguous input cases → add an `ask_user` tool.
   - 10% are really hard cases → accept or move to a more powerful model.

2. **One change at a time.** Improve one thing, re-measure. If you change 5 things together and it improves 3%, you don't know what worked.

3. **Keep a changelog.**
   ```
   2026-04-12  v3 prompt: added escape hatch       pass: 70 → 78
   2026-04-15  v3+ structured output JSON          pass: 78 → 86
   2026-04-20  v3+ ask_user tool                   pass: 86 → 91
   ```
   When a change makes things worse, you know which and can roll back.

4. **Resist the temptation to upgrade the model.** Often 2 hours of prompt engineering beats 10x cost from a bigger model.

## 14.9 Eval for multi-step agents

For agents doing action sequences (e.g. search + synthesis + email), evaluate:

- **End-to-end**: is the final task correctly completed?
- **Step-level**: is each intermediate step correct?
- **Trajectory**: is the order and number of steps reasonable?
- **Tool selection**: did it use the right tools?

Don't only look at the final output. An agent that "guessed" the right final answer after using 20 useless tools is less robust than one that finds it in 3 steps.

## 14.10 Practice: 3 cycles of eval-improve

Exercise to fix the pattern:

1. **Basic setup**: a simple agent (e.g. research assistant on a niche you know).
2. **Dataset**: 20 representative examples, with success criteria.
3. **Run baseline**: measure pass rate.
4. **Analysis**: read the failures, write 3 improvement hypotheses.
5. **Implement the first hypothesis.** Measure.
6. **Implement the second.** Measure.
7. **Implement the third.** Measure.

At the end, write 5 lines on what you learned. The pattern *eval → analyze → change one → re-measure* is the single highest-leverage habit in this entire field.

## 14.11 Key takeaways

- **Without eval, you fly blind.** Build a dataset before the code.
- **Mix of metrics**: programmatic (fast, dual), LLM-as-judge (qualitative, scalable), human (gold standard).
- **Pairwise > absolute scoring** for LLM-as-judge.
- **One change at a time**, changelog, rollback ability.
- **A/B with feature flags** for production changes.
- **Continuous eval**: monitor drift, sample traffic, annotate.
- **Categorize failures** before changing. Often 80% is in 3 patterns.

## 14.12 Common mistakes

- **No eval dataset.** The most common and damaging pattern.
- **Only programmatic metrics.** You miss everything qualitative.
- **Only LLM-as-judge.** Uncontrolled judge bias.
- **Changing 10 things together.** You don't know what works.
- **Eval only before deploy.** Quality degrades over time (drift), you don't notice.
- **Confusing pass rate with real quality.** A bad dataset gives high pass rate on a bad agent.

---

You have the tools to measure and improve. Now we close with a panorama of **where agents are changing real work**.

→ [Chapter 15 — Real use cases and workflows](15-casi-uso-e-workflow-reali.md)
