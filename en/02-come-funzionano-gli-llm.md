# 2. How LLMs Work (the engine)

To use an agent well, you need to know what's happening *inside* its engine — the LLM. You don't need the math, you need the **right intuition**.

## 2.1 What an LLM does, in one sentence

> Given a piece of text, it predicts the most probable next piece of text.

That's it. Literally. A model like GPT-5, Claude 4 or Gemini 2 has one super-power: given an input, predict what comes next.

```
Input:  "The sun rises in the..."
Model:  predicts "east"
```

When it seems to "reason," "write poems," "explain code," it's actually always doing the same thing: predicting subsequent tokens, one at a time, with calculated probability.

The magic is that, trained on billions of documents, the pattern "what's the plausible next word" covers almost everything: translation, summary, reasoning, code. Not because it truly understands, but because it has seen a vast number of examples of "how a text starting like this continues."

## 2.2 Tokens: the LLM currency

An LLM doesn't work with characters or words, but with **tokens**. A token is a piece of text, usually 3-4 characters or a short word.

```
"Hello, how are you?"  →  ["Hello", ",", " how", " are", " you", "?"]   (6 tokens)
"Antidisestablishment" →  ["Anti", "dis", "establ", "ishment"]          (4 tokens)
```

Why does this matter to you?

1. **Everything is measured in tokens.** API costs are calculated in tokens (input + output). A model's "context window" is measured in tokens.
2. **Tokens ≠ words.** A non-English text "occupies" more tokens than English at equal word count, because tokenizers are optimized on English. Rule of thumb: 1 English word ≈ 1.3 tokens; 1 Italian word ≈ 1.5-2 tokens.
3. **The model only sees tokens.** If you change even a comma, the input changes. In prompt-engineering tricks (Ch. 5) this matters.

Practical tool: [OpenAI's tokenizer](https://platform.openai.com/tokenizer) shows you how a text is "split" into tokens.

## 2.3 The context window

The **context window** is the maximum number of tokens the model can "see" in a single turn: input + output combined.

Typical numbers in 2026:
- Claude 4.7 Opus: **1M tokens** (≈ 750,000 words, roughly two copies of *War and Peace*).
- GPT-5: in the order of 200K-400K tokens depending on the plan.
- Gemini 2: up to 2M tokens in specific versions.

What does this mean for you?

- You can put an entire book, codebase, month of chat into the prompt.
- **More context ≠ always better**. Beyond a certain threshold the model "loses attention" on parts of the prompt (effect known as *lost-in-the-middle*).
- **More context = more cost and slower.** Every input token must be processed.

Practical rule: use the context you need, not all you have available.

## 2.4 Sampling: why the same prompt gives different answers

When the model predicts the next token, it actually computes a **probability distribution** over all possible tokens. E.g.:

```
Input: "The color of the sky is..."
   "blue"   → 38%
   "azure"  → 35%
   "gray"   → 8%
   "pink"   → 0.1%
   ...
```

At this point one of the candidates must be **picked**. The main sampling parameters are:

- **Temperature** (0.0 - 2.0): how "creative" the model is.
  - `0.0` = always picks the most probable (deterministic, repetitive).
  - `0.7-1.0` = balanced (typical default).
  - `>1.2` = bold choices, sometimes ungrammatical.

- **Top-p** (0-1): considers only the tokens that cumulatively reach p% probability. E.g. top-p=0.9 = ignores tokens in the "long tail" of improbabilities.

- **Top-k**: considers only the top k most probable tokens.

- **Seed**: some models accept a seed to make sampling reproducible (useful in tests).

**Practical implication for agents:** when you want decisive, structured behavior (e.g. the agent picks a tool to call), lower the temperature (`0.0-0.3`). When you want creativity (brainstorming, writing), raise it (`0.7-1.0`).

## 2.5 The structure of an interaction (chat)

Modern APIs use a **message** format with roles:

```python
[
  {"role": "system", "content": "You are an expert assistant on Italian cuisine."},
  {"role": "user", "content": "How do you make carbonara?"},
  {"role": "assistant", "content": "You'll need guanciale, pecorino..."},
  {"role": "user", "content": "Can I use pancetta?"},
]
```

Three main roles:

- **system**: the base instructions, "who you are and how to behave." They persist throughout the conversation. The system prompt is where you shape the agent's behavior.
- **user**: the user's messages.
- **assistant**: the model's responses (also historical, to give it memory of the conversation).

When you add **tool use** (Ch. 6), other roles/structures are added: `tool_use` (the model calls a function) and `tool_result` (result returned to the model).

## 2.6 What an LLM does well

- Summarize, rephrase, translate.
- Extract structured information from unstructured text.
- Write code (with limits — see below).
- Classify ("is this spam? is it positive or negative?").
- Follow complex multi-step instructions when well-formulated.
- Reason step by step (especially models with "thinking" / chain-of-thought).

## 2.7 What it does NOT do well (limits to know)

- **Complex arithmetic.** It doesn't have a calculator inside: sometimes guesses, sometimes doesn't. For serious numbers, give it a tool with Python.
- **Rare or recent factual truths.** The model has a *knowledge cutoff* (date of last training). For up-to-date or niche facts, you need RAG (Ch. 7) or web search.
- **Coherence over very long contexts.** Even with 1M tokens it can lose details.
- **Precise counts.** "How many 'r' are in strawberry?" is famously hard for them — because they see tokens, not letters.
- **Saying "I don't know".** Often it prefers to invent (the phenomenon called **hallucination**). See Ch. 13.
- **Rigorous causal reasoning.** It's good at *seeming* to reason, but on novel problems outside training it often fails.

## 2.8 Models and families (2026 overview)

The main LLM "providers":

| Family | Companies | Strengths |
|---|---|---|
| **Claude** (Anthropic) | Opus, Sonnet, Haiku | Coding, long-form reasoning, safety, long contexts |
| **GPT** (OpenAI) | GPT-5, GPT-5 Mini | Ecosystem, mature tool use, ChatGPT plugins |
| **Gemini** (Google) | Gemini 2 Pro/Flash | Multimodality (audio/video), huge context windows |
| **Llama** (Meta) | Llama 4, various sizes | Open weights, self-hosted |
| **Mistral** (Mistral AI) | Mistral Large, Mixtral | Open weights, excellent European models |
| **Qwen, DeepSeek** | various | Open models, very competitive |

Each family has different-sized models, with the classic tradeoff:
- **Large models** (Opus, GPT-5, Gemini Ultra): more capable, more expensive, slower.
- **Small models** (Haiku, Mini, Flash): less capable but much cheaper and faster. Often enough.

Practical agent rule: **prototype with the most capable model, in production switch to the smallest one that maintains acceptable quality**. You save 5-10x on costs.

## 2.9 Practice: feel the difference

Go to [chat.openai.com](https://chat.openai.com) or [claude.ai](https://claude.ai) and try these three experiments:

1. **Count the 'a's in "abracadabra".** If the model gets it wrong, you've seen the token problem.
2. **Ask: "Calculate 837 × 924 without using tools."** Compare with the actual result (773,388). They often get it wrong.
3. **Ask the same thing twice:** "Invent a name for a literary café." You'll see different answers — that's sampling at work.

It will give you intuition no chart could.

## 2.10 Key takeaways

- **The LLM predicts tokens, one at a time.** Everything else flows from this simple thing.
- **Token = unit of measurement.** Costs, context, performance: everything is in tokens.
- **Temperature regulates creativity.** Low for decision-making agents, high for writing.
- **System prompt > user prompt** for shaping baseline behavior.
- **Big models aren't always needed.** Start big, optimize small.
- **Knowing the limits** (math, recent facts, counts) saves you from nasty surprises.

## 2.11 Common mistakes

- **Thinking the model "knows" something.** It knows patterns, not facts. For facts, give it sources (RAG, tools).
- **Using high temperature for decision-making agents.** Result: the agent changes its mind, picks wrong tools, loops.
- **Filling the context window for safety.** More context = more noise. Put only what's essential.
- **Sticking to one model "because it works".** Different models are good at different things. Test more than one for your use case.

---

Now that you know what the engine looks like, let's see how the agent's **chassis** is built around it.

→ [Chapter 3 — Anatomy of an agent](03-anatomia-di-un-agente.md)
