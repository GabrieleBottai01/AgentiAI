# 02 — Complete tool design

Reference: **Chapter 6** of the guide.

> 🇮🇹 [Versione italiana](README.it.md)

## What you'll learn

- How to write tool descriptions the model actually understands (including "when NOT to use them").
- Precise JSON Schema with `enum`, `maxLength`, `required`.
- **Structured error handling**: tools always return `{ok: true/false, ...}`, never raise.
- **Idempotency keys** for tools with side effects (sending email).
- **Truncating** tool output so it doesn't flood the context window.

## What it does

The agent is given an outreach task: find every enterprise user, send each of them a personalised email, then summarise.

You'll see:
1. `search_users(tier="enterprise")` → returns the filtered list.
2. For each user, `send_email(to=..., subject=..., body=..., idempotency_key=...)`.
3. A final summary with the number of emails sent.

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## What to notice in the code

- `search_users.description` explicitly states what to do and what NOT to do. This is **the** most important prompt for a tool.
- `send_email` takes an optional `idempotency_key`, but the system prompt forces the model to pass it.
- `execute_tool()` catches `TypeError` and returns a structured error — the agent reads the error and can retry with corrected arguments.
- Output is truncated at 4000 characters to avoid saturating the context window.

## Exercise for you

1. Add a `get_user_by_id(id)` tool with a precise purpose (exact lookup, not search).
2. Change the system prompt to make the agent **show a dry run** before sending (ask for confirmation in text).
3. Extend `_USERS` to 50 users and watch how the agent handles the larger volume.
