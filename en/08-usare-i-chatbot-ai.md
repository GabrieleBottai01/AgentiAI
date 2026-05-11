# 8. Using AI Chatbots: ChatGPT, Claude.ai, Gemini

Before building agents, learn to **use them well** on consumer products. It's the fastest way to develop intuition on what works and what doesn't, and for many real-life tasks it's also all you need.

## 8.1 The three main interfaces

| Product | URL | Maker | Strengths |
|---|---|---|---|
| **ChatGPT** | chat.openai.com | OpenAI | Richest ecosystem (GPT, Plugins, Code Interpreter, custom GPTs) |
| **Claude** | claude.ai | Anthropic | Excellent for writing/coding, long contexts, "Projects" |
| **Gemini** | gemini.google.com | Google | Google integration (Gmail, Docs, Drive), multimodality |

All three offer:
- Limited free tier.
- Paid tier (~€20/month) with more capable models and higher limits.
- Mobile and desktop apps.

Practical differences change often. Your choice should be based on:
- **Which ecosystem you already use** (Google Workspace? → Gemini integrates well).
- **What you use it for** (intense writing/coding? → Claude tends to win).
- **Which UX you like**.

Trying all three for two weeks is the most sensible thing.

## 8.2 The features that change life

All three offer, with different names, these features:

### Memory
ChatGPT "Memory", Claude "Project knowledge", Gemini "Saved info". Save facts about you between conversations.

**What to put in:**
- Your role, preferred tone ("answer in English, direct style").
- Your team's conventions (language, libraries, frameworks).
- Persistent constraints ("I use macOS, prefer Python 3.12").

**What NOT to put in:**
- Secrets, passwords, sensitive data (providers can use conversations for training, unless opted out).
- Information that changes often (you'll rewrite it every time).

### Attachments and files
You can upload PDFs, images, Excel sheets, code. The model reads them and reasons about them.

**Typical use cases:**
- "Summarize this 80-page PDF."
- "Extract this invoice's data into CSV."
- "Anything strange in this chart?" (multimodal: image + reasoning).

**Limit:** very large PDFs may saturate context or be processed in chunks. For document libraries, RAG (Ch. 7).

### Code execution / Code Interpreter
The model writes and **runs Python code** in a sandbox to:
- Analyze a CSV.
- Generate charts.
- Convert file formats.
- Do precise calculations.

This is the "code-generating agent" we talked about in Ch. 4. Very fast for data-driven tasks.

### Web search
The model searches the web during the response. Essential for up-to-date facts (beyond knowledge cutoff).

ChatGPT, Claude and Gemini all have this function. Activates by default when the model "feels" it's needed, or via an explicit toggle.

### Image generation
Generates images from prompts. From visual identity for slide decks to UI mockups. Quality varies: DALL-E 3 in ChatGPT, Imagen in Gemini, Sora for video.

### Voice / conversation mode
Mobile app: you talk, the model answers with voice. Surprisingly good, great for long prompts while walking.

### Custom GPTs / Projects / Gems
"Configured" versions of the AI with dedicated prompts and knowledge. Examples:
- ChatGPT Custom GPT with specialized instructions (e.g. "my writing coach", "Italian law expert").
- Claude Project with a set of uploaded documents (e.g. all 2025 contracts).
- Gemini Gem with a customized role.

They are the simplest way to "build an agent" without writing code.

## 8.3 Recommended workflows

### Workflow 1 — Brainstorming
1. Open a new chat.
2. Explain the problem in 3-4 sentences, give context on your target.
3. Ask for 10 ideas, each with "why it could work" and "risks".
4. Pick a shortlist of 3 and ask to deepen them.
5. For the favorite, ask for an execution plan.

### Workflow 2 — Writing (article, email, post)
1. Explain: topic, audience, tone, length, format.
2. Ask for an **outline** before the full text.
3. Iterate on the outline until it convinces you.
4. Only then ask for the full text.
5. Editing: ask "make it more direct", "remove adjectives", "add an example in paragraph 3".

Skipping the outline is the most common mistake. The model will write 1000 words on an angle you don't like, and you'll have more trouble rewriting than starting over.

### Workflow 3 — Document analysis
1. Upload the document.
2. Start with: "Summarize in 5 bullets" → calibrates you on the content.
3. Targeted questions: "What does it say about section X?", "What are the deadlines?".
4. Structured extraction: "Extract dates in YYYY-MM-DD format, one per line".

### Workflow 4 — Learning a new topic
1. "Explain X to me as if I were new. Start with context, then key concepts, then an example."
2. "Now test me: ask 5 questions in increasing difficulty."
3. You answer, it corrects.
4. "What are the typical misconceptions of someone starting with X?"
5. "Best resource to go deeper?" (verify suggested links — can invent).

### Workflow 5 — Coding (light)
1. Describe the problem with an example of desired input/output.
2. Specify language, library, constraints (no external dependencies, etc.).
3. Ask for code + explanation.
4. Test: copy in an editor, run. If it doesn't work, show the error to the model.
5. For serious projects, switch to Claude Code (Ch. 9), not chat.

## 8.4 Tips that make a difference

- **Start every chat with context.** "I'm a civil lawyer, this document's user is a non-technical client." Changes all quality.
- **One chat = one topic.** Open a new chat for a new task. Mixing confuses the model and your memory.
- **Save good prompts.** If you find a prompt that works, put it in a note. It'll come in handy.
- **Use "Continue" or "Expand"** if the response is incomplete.
- **"Critique your response"** before accepting. Often things that were missing emerge.
- **Compare models** on the same prompt when in doubt. ChatGPT and Claude can give different useful perspectives.
- **For repetitive tasks**, create a Custom GPT / Project / Gem. You reuse prompts and context without repeating each time.

## 8.5 What NOT to do

- **Don't paste sensitive data.** Tax IDs, credentials, confidential business IP: use opt-out training mode, or enterprise products (ChatGPT Enterprise, Claude Team) with no-training policy.
- **Don't trust links.** Models invent plausible URLs that don't exist. Always verify.
- **Don't delegate critical decisions** without verification. Medical diagnoses, legal advice, financial: AI is a support tool, not a decider.
- **Don't expect coherence between turns**. If you ask the same thing twice with small variations, it can answer differently. It's normal.
- **Don't fight the model.** If it doesn't get it after 3 attempts, rephrase or switch to another model.

## 8.6 Privacy and training: what you need to know

By default, providers can use your conversations to improve models. To avoid:

- **ChatGPT**: Settings → Data Controls → "Improve the model for everyone" → OFF.
- **Claude**: Pro conversations aren't used for training by default. Verify in settings.
- **Gemini**: Activity → Web & App Activity → check what gets saved.

For professional use, prefer Enterprise/Team versions with non-training SLAs written in the contract.

## 8.7 Exercise: the "day's test"

For one week, every time you're about to do something that requires thinking or writing, ask yourself: **"can I do it with AI first?"**. Don't blindly delegate, but use it as an **accelerator**.

List of typical tasks where it changes everything:

- Write a difficult email (warning to a supplier, condolences, awkward request).
- Take notes from a meeting (audio → text → summary + action items).
- Analyze a 50-row Excel (ask to find patterns).
- Translate a technical text (curate the glossary).
- Explain a concept to your kid simply.
- Generate 10 names for a project.
- Summarize a long article.
- Validate an idea ("find the 5 biggest holes in this proposal").

After a week you'll have a natural intuition of "when AI suits me."

## 8.8 Key takeaways

- **ChatGPT, Claude, Gemini** are the starting point. Try them, pick the one that fits your work best.
- **Memory, attachments, code interpreter, web search**: the cross-cutting features you use daily.
- **Workflow > single prompt**. Outline before text, brainstorming before solution, summary before detailed questions.
- **Custom GPT / Project / Gem** for repetitive tasks: configure once, reuse always.
- **Privacy**: opt-out training, never sensitive data, prefer Enterprise for professional use.

## 8.9 Common mistakes

- **Expecting results without giving context.** "Write me an email" → mediocre. "Write me an email to a B2B client complaining about delay, cordial but firm tone, in English" → excellent.
- **Sticking with single prompt.** The next 5 responses refine your result.
- **Looking for the magic phrase.** It doesn't exist; a good workflow does.
- **Using ChatGPT for serious coding.** Great for snippets; for projects, Claude Code or Cursor are more productive.
- **Not exploiting voice mode** for thinking aloud. You walk, talk, get answers. Changes how you work.

---

Chatbots are the "consumer" level. For developers, something much more powerful exists: an AI agent inside your terminal.

→ [Chapter 9 — Claude Code for developers](09-claude-code-per-sviluppatori.md)
