# 15. Real Use Cases and Workflows

In this chapter no new theory. Just **where agents are changing real work**, with patterns you can adopt. Think of it as a menu to pick your next project from.

## 15.1 Coding and software development

### Intensive pair programming
Tools: Claude Code, Cursor, Aider, Windsurf.

What changes: the speed of writing "boilerplate" code (CRUD, integrations, mechanical refactors) plummets. Devs focus on **architecture, edge cases, code review**.

Typical pattern:
1. Write a spec (the "what" and "why").
2. The agent proposes plan + diff.
3. You review, correct, iterate.
4. Tests run automatically.
5. Commit.

Realistic result: 2-4x productivity on standard tasks, marginal on truly new problems.

### Automatic code review
Agent that runs on every PR and comments on:
- Potential bugs.
- Patterns inconsistent with the rest of the codebase.
- Missing tests.
- Security issues (SQL injection, hardcoded secrets).

Examples: GitHub Copilot Code Review, Anthropic `/ultrareview`, CodeRabbit.

### Debug and incident response
Agent that, given a log or stack trace:
- Identifies the probable cause.
- Searches relevant code.
- Proposes a fix.

In on-call, reduces "time to first hypothesis" from 30 minutes to 1.

### Migration and refactor
Real examples: Python 2 → 3, AngularJS → React migration, monolith → microservices.

Approach:
1. The agent analyzes the codebase, maps patterns.
2. Proposes a migration strategy.
3. Executes small steps, with tests at each step.
4. Human reviews, approves.

For big projects, agents like Devin, Coursive, or dedicated frameworks can work autonomously for days.

## 15.2 Customer support

### Automatic Tier-1
Agent handling ~70% of standard questions:
- FAQ.
- Order status.
- Password reset.
- Data change.

When it doesn't know, **escalate** to a human with context already prepared.

Pattern:
- RAG on the company knowledge base.
- Tools for CRM, order system, billing.
- Conversation memory for continuity.
- Confidence threshold: below X, escalate.

### Triage and classification
Agent reading incoming tickets and:
- Classifying (billing, tech support, sales).
- Assigning priority.
- Routing to the right team.
- Suggesting the first response to the human agent.

Reduces triage time by 80-90%.

### Conversation summary
After a long conversation, the agent produces:
- Summary.
- Action items.
- Customer sentiment.
- Follow-up suggestions.

## 15.3 Research and analysis

### Deep research
Tools like ChatGPT Deep Research, Perplexity Pro, Gemini with Workspace.

Pattern:
1. Complex question ("analyze the X market over the last 5 years").
2. Agent navigates the web, reads dozens of sources, cross-checks.
3. Produces a structured report with citations.

Work that required 1-2 days of a junior analyst is done in 30 minutes, with quality sufficient for first draft.

### Data analysis
ChatGPT Code Interpreter, Claude with `code_execution` tool, Hex Magic, Julius AI.

Pattern:
1. Upload a CSV/Excel.
2. Explain what you want to understand.
3. The agent writes Python, executes, produces charts.
4. Continue the conversation: "now segment by region", "do statistical test", "export Excel".

For exploratory analysis it's a revolution.

### Document review
For legal, finance, due diligence:
- Upload a set of contracts / documents.
- Agent extracts specific clauses, flags anomalies, compares with templates.
- Produces a checklist to review.

Tools: Harvey, Hebbia, Legora (legal); Hebbia, Anvilogic (finance/security).

## 15.4 Writing and content

### Long-form writing
Pattern that works:
1. Clear brief: topic, audience, tone, length.
2. Outline before text.
3. Iterations on the outline.
4. Section-by-section expansion.
5. Final editing (human or assisted).

For blog posts, articles, guides: half a day of human work reduces to an hour of review.

### Newsletter and periodic briefs
Agent that every morning:
- Reads the sources you follow.
- Synthesizes into 5 bullets.
- Sends via email.

Basic setup: 100 lines + cron + LLM.

### Localization
Translation + cultural adaptation of web content, manuals, e-commerce. Specialized agents with corporate glossaries reach final-editing quality, no longer rebuilding.

## 15.5 Operations and automation

### Email management
Always-on agent (Ch. 4) that:
- Classifies incoming emails.
- Replies to repetitive ones (automatic or with draft).
- Extracts action items into a task manager.
- Flags urgent ones.

Tools: Superhuman AI, Shortwave, custom agents on Gmail API.

### Calendar and scheduling
Agent that, given a goal ("meeting with Marco and Giulia by Friday"), finds slots, sends invites, manages conflicts, reschedules.

Consumer tools: Reclaim, Motion. For companies: custom agents on Outlook/Google Calendar.

### Process automation
Business-as-usual workflows with agents that orchestrate heterogeneous steps:
- Customer onboarding: read docs, validate them, create account, send welcome.
- Procurement: request → quotes → comparison → order.
- Reporting: collect data from N sources, format, send.

Pattern: orchestrator + specific tools for each system.

## 15.6 Sales and marketing

### Lead enrichment
Agent that, given a raw lead (email, company):
- Searches public info.
- Profiles the company (sector, size, buy signals).
- Suggests outreach angle.

Tools: Clay, Apollo, Crystal.

### Personalized outreach
Generation of 1:1 messages based on:
- Prospect profile.
- Your product.
- Applicable use case.

Caution: without human touch, falls into spam. Best practice: AI does the draft, human refines.

### Content velocity
From one cue, the agent produces: LinkedIn post, X thread, blog post, newsletter. Each channel with adapted tone.

## 15.7 Education and training

### Personalized tutors
Khanmigo (Khan Academy), Duolingo Max, corporate GPT-tutors.

Pattern:
- Student asks.
- The agent doesn't give the answer, asks Socratic questions.
- Adapts difficulty to the level.
- Keeps memory of progress.

### Corporate onboarding
New hires chat with an agent that has access to all internal documentation. Typical questions ("how do you do X?") answered 24/7 without bothering colleagues.

### Simulated training
Agents impersonating difficult customers, candidates in interview, crisis situations. Trainees practice safely.

## 15.8 Healthcare (with caution)

Cases that work today:
- **Clinical documentation**: listening to a consultation, generating SOAP notes, ICD coding. Tools: Abridge, Suki, Nuance DAX.
- **Primary triage**: chatbot directing to specialist or ER. Under clinical supervision.
- **Paper research**: synthesis of medical literature for the clinician.

Cases that don't work today:
- **Autonomous diagnosis**: huge risks, complex regulation.
- **Therapeutic decisions**: AI assists, doctor decides.

Rules: in EU the AI Act classifies many medical applications as "high risk" → requires specific certifications.

## 15.9 Legal and compliance (with caution)

Cases that work:
- **Contract review**: clause extraction, comparison with templates, flag anomalies.
- **E-discovery**: analysis of large document volumes for litigation.
- **Legal research**: case law search, judgment summaries.
- **Drafting standard clauses**: lawyer refines.

Caveat: AI can invent case law. Mandatory verification. Famous cases of lawyers sanctioned for presenting non-existent rulings generated by ChatGPT.

## 15.10 More "agentic" cases

Examples of products pushing the autonomy level:

- **Devin** (Cognition): coding agent that works autonomously for hours, completing complex tasks.
- **OpenAI Operator** / **Anthropic Computer Use**: agents that use browser/desktop like a human (see screen, click, type).
- **Replit Agent**: build full-stack apps from prompts.
- **AutoGPT, BabyAGI** (early): first attempts at generalist agents, with results more demonstrative than productive.
- **Aria** (Opera), **Arc Search**: native-AI browsers.

They are often still **impressive demos** that betray fragility in production. The direction is clear, the maturation speed isn't.

## 15.11 Cross-cutting patterns

Regardless of domain, winning workflows share:

1. **Human-in-the-loop on costly decisions.** AI does most, human validates the critical.
2. **Structured briefs** instead of free prompts.
3. **Concrete tools** to talk to real systems (CRM, DB, API).
4. **RAG** to make the agent speak with authority on specific data.
5. **Context memory** so as not to repeat setup every time.
6. **Measurement** of output and outcome.
7. **Disclosure** that it's AI-generated when relevant.

## 15.12 When NOT to add agents

Worth remembering:

- If the workflow is simple and codified, traditional automation is better.
- If the error is unacceptable and there's no human verification, careful.
- If the data is too sensitive and you don't have dedicated infra, wait.
- If costs aren't justified, don't scale.

AI is a multiplier, not a replacement of judgment.

## 15.13 To pick as your next project

If you're starting and want a project to do to learn, here's a list in order of ease:

1. **Q&A bot on your PDF** (RAG + chat). 1-2 hours. Ch. 7, 10.
2. **Automatic summary of your day's emails**. 2-3 hours. Email tool + LLM.
3. **CSV analysis agent**. 3-4 hours. Code interpreter pattern.
4. **Customer support on company FAQ**. 1-2 days. RAG + dev deploy.
5. **Coding agent specialized for your stack**. 1-2 weeks. Claude Agent SDK + custom tools.

Starting to do > reading another 100 pages.

## 15.14 Key takeaways

- **Coding, support, research, writing, ops, sales, education**: agents are changing everything.
- **Cross-cutting patterns**: structured brief, tools, RAG, human-in-the-loop, measurement.
- **High-stakes domains (health, law, finance)**: assistance yes, autonomy no.
- **Impressive demo ≠ robust production.** Always verify.
- **Start from a small, personal project.** Living an end-to-end agent is more formative than 10 courses.

## 15.15 Common mistakes

- **"AI will solve X."** Without concrete patterns and workflows, it doesn't.
- **Building the most ambitious agent on the first try.** Frustration guaranteed.
- **Neglecting integration**. Agent quality depends on the quality of tools and data you give it.
- **Launching without measuring real impact.** "The user is happy" without data.
- **Not capitalizing on existing workflows.** AI shines when it slips into processes you already do, not when you have to reinvent them.

---

Last chapter: the glossary to remember terms, and a list of resources to go beyond the guide.

→ [Chapter 16 — Glossary and resources](16-glossario-e-risorse.md)
