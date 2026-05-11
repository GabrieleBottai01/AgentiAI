"""
Esempio 02 — Tool design completo
Capitolo 6 della guida.

Mostra:
- Schema preciso (enum, descrizioni, vincoli).
- Multiple tools, descrizioni che spiegano "quando usare / quando NON usare".
- Error handling strutturato (no exceptions, sempre risultato JSON-friendly).
- Idempotency key per tool con effetti collaterali.
- Truncation dell'output dei tool.

Esegui: python main.py
"""

import json
import os
from datetime import datetime, timezone
from anthropic import Anthropic


# ----- "Database" in-memory per la demo -----
_USERS = {
    "u-001": {"name": "Mario Rossi", "email": "mario@example.com", "tier": "pro"},
    "u-002": {"name": "Giulia Bianchi", "email": "giulia@example.com", "tier": "free"},
    "u-003": {"name": "Lucia Verdi", "email": "lucia@example.com", "tier": "enterprise"},
}
_SENT_EMAILS = {}  # idempotency_key → record


# ----- Tool implementations (sempre JSON-friendly, mai exception) -----
def search_users(query: str = "", tier: str = "any", limit: int = 10) -> dict:
    """Cerca utenti per nome/email; filtra per tier."""
    matches = []
    for uid, u in _USERS.items():
        if query and query.lower() not in u["name"].lower() and query.lower() not in u["email"].lower():
            continue
        if tier != "any" and u["tier"] != tier:
            continue
        matches.append({"id": uid, **u})
    matches = matches[: max(1, min(50, limit))]
    return {"ok": True, "count": len(matches), "results": matches}


def send_email(to: str, subject: str, body: str, priority: str = "normal",
                idempotency_key: str = "") -> dict:
    """Invia email (simulato). Idempotente se idempotency_key fornito."""
    if not to or "@" not in to:
        return {"ok": False, "error": f"email destinatario non valida: {to!r}"}
    if priority not in ("low", "normal", "high"):
        return {"ok": False, "error": f"priority non valida: {priority!r}"}
    if idempotency_key and idempotency_key in _SENT_EMAILS:
        return {"ok": True, "status": "already_sent", "key": idempotency_key,
                "message_id": _SENT_EMAILS[idempotency_key]["message_id"]}

    msg_id = f"msg-{datetime.now(timezone.utc).timestamp():.0f}"
    rec = {"to": to, "subject": subject, "body": body[:500], "priority": priority,
           "message_id": msg_id, "sent_at": datetime.now(timezone.utc).isoformat()}
    if idempotency_key:
        _SENT_EMAILS[idempotency_key] = rec
    return {"ok": True, "status": "sent", "message_id": msg_id}


# ----- Tool schemas (the prompt that drives the model's choice) -----
TOOLS = [
    {
        "name": "search_users",
        "description": (
            "Cerca utenti nel database. Usa per: trovare un utente specifico per nome/email, "
            "o elencare utenti di un certo tier. NON usare per: modificare utenti, statistiche aggregate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Stringa da cercare nel nome o email. Vuoto per nessun filtro."
                },
                "tier": {
                    "type": "string",
                    "enum": ["any", "free", "pro", "enterprise"],
                    "description": "Filtra per livello account. 'any' (default) = nessun filtro."
                },
                "limit": {
                    "type": "integer",
                    "description": "Massimo risultati (1-50). Default 10."
                },
            },
        },
    },
    {
        "name": "send_email",
        "description": (
            "Invia una email transazionale a un destinatario. Usa per: notifiche, "
            "conferme, password reset. NON usare per: marketing o spam. "
            "IMPORTANTE: passa sempre 'idempotency_key' per evitare invii duplicati su retry."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Indirizzo email destinatario (es. mario@example.com)."
                },
                "subject": {
                    "type": "string",
                    "description": "Oggetto della email, max 100 caratteri.",
                    "maxLength": 100,
                },
                "body": {
                    "type": "string",
                    "description": "Corpo della email in testo plain o markdown."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high"],
                    "description": "Priorità di invio. Default 'normal'."
                },
                "idempotency_key": {
                    "type": "string",
                    "description": "Chiave univoca per questa email logica (es. 'welcome-u001-2026-05-07'). "
                                    "Garantisce non doppi invii in caso di retry."
                },
            },
            "required": ["to", "subject", "body"],
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """Esegue il tool e tronca l'output. Mai exception verso l'agente."""
    try:
        if name == "search_users":
            result = search_users(**args)
        elif name == "send_email":
            result = send_email(**args)
        else:
            result = {"ok": False, "error": f"tool sconosciuto: {name}"}
    except TypeError as e:
        result = {"ok": False, "error": f"argomenti invalidi: {e}"}

    out = json.dumps(result, ensure_ascii=False)
    return out[:4000]  # truncation


def run_agent(client: Anthropic, goal: str, max_iterations: int = 8):
    messages = [{"role": "user", "content": goal}]
    for step in range(1, max_iterations + 1):
        print(f"\n→ Iter {step}")
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            system=(
                "Sei un agente operativo. Usa i tool con cura. "
                "Per send_email genera SEMPRE un idempotency_key univoco. "
                "Concludi con un riassunto delle azioni svolte."
            ),
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            for b in resp.content:
                if b.type == "text":
                    print(f"\n=== RISPOSTA ===\n{b.text}")
            return

        tool_results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            print(f"  • {b.name}({json.dumps(b.input, ensure_ascii=False)})")
            out = execute_tool(b.name, b.input)
            print(f"    → {out[:200]}")
            tool_results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
        messages.append({"role": "user", "content": tool_results})


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Errore: imposta ANTHROPIC_API_KEY"); return

    client = Anthropic(api_key=api_key)
    goal = (
        "Trova tutti gli utenti enterprise e mandagli una email con oggetto "
        "'Aggiornamento mensile prodotto' e un breve corpo che li ringrazia. "
        "Dimmi alla fine quante email hai inviato."
    )
    print(f"OBIETTIVO: {goal}\n")
    run_agent(client, goal)


if __name__ == "__main__":
    main()
