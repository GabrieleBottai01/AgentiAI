# 5. Prompt Engineering: the Art of Asking

> "Prompt engineering is 80% of the work to make an agent function well. The remaining 20% is choosing the right model and giving it the right tools."

Learning to write effective prompts is the highest-leverage skill in this entire field. It applies to those who use ChatGPT, those who build agents, those who configure a customer support system.

## 5.1 What a "prompt" really is

A prompt is **all the text the model sees before responding**. It includes:

- The **system prompt** (base instructions, "who you are and how you behave").
- The **user message** (the current request).
- The **history** (previous turns, if it's a conversation).
- The **tool results** (output of tools in past turns).
- Any **documents** you've attached.

When I say "the prompt," I often mean all this together. The model doesn't distinguish: for it, it's one large sequence of tokens.

## 5.2 The structure of a good prompt

A well-crafted prompt almost always has these pieces, in this order:

1. **Role** — who is the model?
2. **Goal** — what should it achieve?
3. **Context** — background information
4. **Constraints** — what it must / must not do
5. **Output format** — how I want the response
6. **Examples** (optional but powerful)

Bad example:

> "Summarize the text I send you."

Good example:

> You are an editor for a scientific magazine. Your job is to summarize academic papers for non-expert readers.
>
> Goal: synthesize the input paper so a law graduate can understand it.
>
> Constraints:
> - Maximum 200 words.
> - No technical jargon that isn't explained.
> - End with a bullet list of "3 practical implications".
>
> Format:
> ## Summary
> [continuous text]
>
> ## Practical implications
> - point 1
> - point 2
> - point 3
>
> Paper: """{paper}"""

The quality difference is enormous.

## 5.3 Fundamental techniques

### 5.3.1 Few-shot prompting

Show the model 2-3 examples of desired input/output. Its subsequent responses will follow the same pattern.

```
Classify tweet sentiment as positive, negative or neutral.

Tweet: "I love this new phone!"
Sentiment: positive

Tweet: "Slowest shipping ever, never again."
Sentiment: negative

Tweet: "Arrived as described."
Sentiment: neutral

Tweet: "The design is ok but the battery dies fast."
Sentiment:
```

The model will complete with `negative` (or `neutral` if cautious). Simple pattern, very high effectiveness.

### 5.3.2 Chain-of-Thought (CoT)

Ask the model to **reason step by step before** answering.

```
Question: Mark has 12 apples. He gives 3 to his sister, eats 2,
then buys double what he has left. How many does he have at the end?

Think step by step before answering.
```

Without CoT, models often get math problems wrong. With CoT, accuracy improves dramatically.

Modern models (Claude with "extended thinking", o5/o7 from OpenAI) do CoT internally *without* you asking. But on smaller models or for hard tasks, telling them "reason step by step" remains useful.

### 5.3.3 Self-consistency

Ask N times the same thing with high temperature, take the most frequent answer. Statistical trick, expensive in tokens, useful on quantitative problems.

### 5.3.4 Decomposition

For complex tasks, divide into explicit sub-tasks:

```
To write this legal report, follow this procedure:

STEP 1: Identify involved parties (name, role).
STEP 2: Summarize the facts in chronological order.
STEP 3: List reference rules.
STEP 4: Write the legal analysis.
STEP 5: Conclude with recommendation.

Execute one step at a time, clearly marking the step number.
```

Models follow explicit procedural structures very well.

### 5.3.5 Role priming

Having the model play a concrete role improves quality for many tasks.

```
You are a Senior Software Engineer with 15 years of experience in distributed systems.
You're code-reviewing a junior. Your style is direct but constructive.
```

It works because the model has seen, during training, millions of examples of "expert X who says Y." By specifying the role, you activate that distribution.

### 5.3.6 Structured output

If you need machine-readable data, ask for it in JSON with an explicit schema:

```
Extract the following info from the CV, in JSON:

{
  "name": "string",
  "years_experience": "number",
  "skills": ["string"],
  "last_role": {
    "company": "string",
    "title": "string",
    "start": "YYYY-MM"
  }
}

Reply ONLY with valid JSON, no extra text.

CV: """{cv}"""
```

Modern APIs offer **JSON mode** or **structured outputs** that guarantee output is valid JSON conforming to the schema. Use them when you can (Ch. 10).

### 5.3.7 Delimiters

When inserting data into the prompt, wrap it in clear delimiters (`"""..."""`, `<doc>...</doc>`). This helps the model distinguish instructions from content, and reduces the risk of **prompt injection** (Ch. 13).

```
Summarize the text below.

<document>
{content}
</document>
```

## 5.4 Common anti-patterns

### "Please" / "I beg you"
They don't hurt, but they don't help. Don't waste tokens on courtesies.

### Vague negations
"Don't be too long" works less than "max 100 words".

### "Be creative" without constraints
The model doesn't know what that means to you. Give concrete examples or constraints.

### Contradictory instructions
"Be precise but not boring. Technical but understandable to all." The model will pick at random.

### Huge prompts without structure
A 4000-word wall of text is hard to follow. Use headings, bullets, sections.

### Changing format without example
"I want output in XML format" without example = lottery. Show what it looks like.

## 5.5 Prompts for agents (specific)

When the prompt goes to an *agent* (not a chatbot), add:

- **List of available tools** and when to use them.
- **Instructions on "when to stop"**.
- **What to do in case of error** or missing info.
- **Format of intermediate responses** (if you want cleanliness).

Example (simplified):

```
You are a research agent. You have these tools:

- web_search(query): search the web. Use for up-to-date facts.
- fetch_url(url): download a page. Use to read specific sources.
- ask_user(question): ask the user in case of ambiguity.

Procedure:
1. Understand the question. If ambiguous, use ask_user BEFORE searching.
2. Search info using web_search. Maximum 3 searches.
3. If results are uncertain, read pages with fetch_url.
4. Synthesize the final response citing sources.

Stop when you have a confident answer. If after 5 iterations you have no
answer, admit it instead of inventing.
```

Notice: giving an **escape hatch** ("admit it instead of inventing") reduces hallucinations. Without it, the model tends to "fabricate" rather than say "I don't know."

## 5.6 Iteration: a prompt is written three times

No one writes a good prompt on the first try. The real flow is:

1. **V1** — write the minimal prompt.
2. **Test** — try with 5-10 representative inputs.
3. **Annotate** where it fails.
4. **V2** — add constraints/examples that address the failures.
5. Repeat.

Keep a versioned `prompts/v3.txt` file. Prompts are code — they deserve git.

## 5.7 Practice: the improving-prompt exercise

Open ChatGPT or Claude.ai and do this:

**Step 1**: ask "Summarize this article" + an article. Annotate the result.

**Step 2**: redo with a structured prompt (role, goal, constraints, format). Annotate.

**Step 3**: add an example of a well-done summary. Redo. Annotate.

You'll see the quality improve at each step. This is the loop you'll do for every agent you build.

## 5.8 Key takeaways

- **Structure > eloquence.** Clear sections beat elegant prose.
- **Examples > explanations.** Showing what you want is more effective than describing it.
- **Structured output (JSON)** when you need data, not text.
- **Delimiters** to separate instructions from user content.
- **Escape hatches** ("if you don't know, say so") reduce hallucinations.
- **Iterate.** The first prompt is almost always suboptimal.

## 5.9 Common mistakes

- **Changing the model hoping to fix prompt problems.** Often the issue is the prompt, not the model.
- **Letting it invent the format.** If you need JSON, ask for JSON with schema.
- **Throwing everything into the system prompt.** Things that change per request go in the user message.
- **Not testing edge cases.** Empty inputs, different languages, contradictory ones, very long ones: the prompt must handle them.
- **Neglecting model version.** A prompt optimized for Claude 3 may not be optimal for Claude 4. Re-test it when you upgrade.

---

Prompts alone aren't enough: agents need **hands and eyes**. Let's see how tools are declared and called.

→ [Chapter 6 — Tool use and function calling](06-tool-use-e-function-calling.md)
