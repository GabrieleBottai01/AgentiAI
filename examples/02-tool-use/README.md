# 02 — Tool design completo

Riferimento: **Capitolo 6** della guida.

## Cosa imparerai

- Come scrivere descrizioni di tool che il modello capisce davvero (incluso "quando NON usarli").
- Schema JSON Schema preciso con `enum`, `maxLength`, `required`.
- **Error handling strutturato**: i tool ritornano sempre `{ok: true/false, ...}`, mai eccezioni.
- **Idempotency key** per tool con effetti collaterali (invio email).
- **Truncation** dell'output dei tool per non saturare il contesto.

## Cosa fa

L'agente riceve un compito di outreach: trova tutti gli utenti enterprise, manda a ognuno una email personalizzata, riassume.

Vedrai:
1. `search_users(tier="enterprise")` → ritorna lista filtrata.
2. Per ogni utente, `send_email(to=..., subject=..., body=..., idempotency_key=...)`.
3. Riassunto finale con numero di email inviate.

## Esegui

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
python main.py
```

## Da notare nel codice

- `search_users.description` cita esplicitamente cosa fare e cosa NON fare. Questo è **il** prompt più importante per il tool.
- `send_email` ha `idempotency_key` opzionale ma il system prompt obbliga il modello a passarlo.
- `execute_tool()` cattura `TypeError` e ritorna errore strutturato — l'agente legge l'errore e può ritentare con argomenti corretti.
- Output truncato a 4000 caratteri per evitare saturazione del context window.

## Esercizio per te

1. Aggiungi un tool `get_user_by_id(id)` con uso preciso (lookup esatto, non ricerca).
2. Modifica il system prompt per chiedere all'agente di **mostrare un dry-run** prima di inviare (chiede conferma in testo).
3. Estendi `_USERS` con 50 utenti e osserva come l'agente gestisce volumi maggiori.
