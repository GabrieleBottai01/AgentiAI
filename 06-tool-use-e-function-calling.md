# 6. Tool use e function calling

I tool sono ciò che trasforma un LLM in un agente. Senza tool, parla. Con i tool, agisce.

## 6.1 L'idea, in una metafora

Pensa a un consulente che lavora da remoto. Sa molte cose, ma per fare il suo lavoro deve poter:

- Leggere documenti che gli mandi.
- Cercare informazioni online.
- Eseguire calcoli.
- Mandare email.

Senza questi accessi, può solo darti consigli generici. Con questi accessi, può davvero **fare cose**.

I tool nei modelli AI funzionano esattamente così: sono **funzioni esterne** che il modello può chiamare quando ne ha bisogno.

## 6.2 Come funziona, in 4 passi

```
1. Tu definisci dei tool, ognuno con: nome, descrizione, parametri.
2. Includi questi tool nella chiamata al modello.
3. Il modello, invece di rispondere subito, può "chiedere": "voglio chiamare X con questi parametri".
4. Tu (il tuo codice) esegui la chiamata e rimandi il risultato al modello.
   Lui prosegue.
```

È **il modello che decide** se e quale tool chiamare. Tu non lo forzi. Lui legge la descrizione del tool e decide se è utile.

## 6.3 Esempio in Python (Anthropic SDK)

```python
from anthropic import Anthropic

client = Anthropic()

tools = [
    {
        "name": "get_weather",
        "description": "Restituisce il meteo attuale per una città. Usa quando l'utente chiede del tempo, della temperatura o se piove.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nome della città, es. 'Roma' o 'New York'"
                }
            },
            "required": ["city"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Devo uscire a Milano, mi serve l'ombrello?"}
    ]
)

print(response.stop_reason)   # 'tool_use'
print(response.content)       # blocco di tipo tool_use con name e input
```

A questo punto il modello **non** ha risposto in testo. Ha detto: "voglio chiamare `get_weather` con `city='Milano'`". Spetta a te eseguire la funzione.

```python
def get_weather(city: str) -> str:
    # qui vera implementazione (chiamata a un'API meteo)
    return f"A {city}: 12°, pioggia leggera"

# Estrai la tool call dalla risposta
tool_use_block = next(b for b in response.content if b.type == "tool_use")
result = get_weather(**tool_use_block.input)

# Rimanda il risultato al modello
follow_up = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Devo uscire a Milano, mi serve l'ombrello?"},
        {"role": "assistant", "content": response.content},
        {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": result
        }]}
    ]
)

print(follow_up.content[0].text)
# "A Milano c'è pioggia leggera, sì, prendi l'ombrello!"
```

Stessa logica con OpenAI SDK, sintassi diversa. I concetti (definire tool con schema, ricevere `tool_call`, ritornare `tool_result`) sono identici.

## 6.4 La cosa più importante: la descrizione

Il modello sceglie quale tool chiamare leggendo la **descrizione**. Se la descrizione è cattiva, sceglierà male.

**Brutto:**
```
"description": "ottiene meteo"
```

**Buono:**
```
"description": "Restituisce il meteo attuale per una città data. Usalo quando l'utente chiede informazioni meteo, temperatura, pioggia, vento, o pianifica attività che dipendono dal tempo."
```

**Eccellente:** aggiungi anche *quando NON usarlo*:
```
"description": "Restituisce il meteo attuale per una città. Usalo per: temperatura, pioggia, vento, condizioni meteo correnti.
Non usarlo per: previsioni a lungo termine (oltre 24 ore), eventi storici, dati climatici medi.
In caso di città ambigua (es. 'Springfield'), chiedi conferma all'utente prima."
```

**Regola d'oro:** scrivi la descrizione del tool come se la stessi spiegando a un nuovo dipendente che deve decidere quando usarlo.

## 6.5 Schema dei parametri: precisione paga

Lo schema dei parametri (JSON Schema) dice al modello *come* costruire la chiamata. Sii preciso:

- `type` (string, number, boolean, array, object).
- `description` per ogni parametro: cosa rappresenta, quale formato.
- `enum` se ci sono valori validi limitati.
- `required` con i campi obbligatori.

Esempio ricco:

```json
{
  "name": "send_email",
  "description": "Invia una email transazionale a un destinatario. Da usare per notifiche all'utente, conferme, password reset. NON usare per email di marketing o spam.",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "description": "Indirizzo email del destinatario, in formato standard (es. mario@example.com)"
      },
      "subject": {
        "type": "string",
        "description": "Oggetto dell'email, max 100 caratteri",
        "maxLength": 100
      },
      "body": {
        "type": "string",
        "description": "Corpo dell'email in formato Markdown. Sarà convertito in HTML."
      },
      "priority": {
        "type": "string",
        "enum": ["low", "normal", "high"],
        "description": "Priorità dell'invio. 'high' solo per password reset e errori critici."
      }
    },
    "required": ["to", "subject", "body"]
  }
}
```

Più lo schema è espressivo, meno il modello sbaglia.

## 6.6 Quanti tool? Quali tool?

**Pochi tool ben fatti > tanti tool generici.**

Errore tipico del principiante: dare 30 tool all'agente. Il modello si confonde, ne sceglie a caso, fa la cosa sbagliata.

Linee guida:

- **5-15 tool** è il range comodo per la maggior parte degli agenti.
- Se ne servono di più, raggruppa: invece di `read_user`, `read_order`, `read_product`, fai un solo `query_db(table, filters)`.
- Per task molto diversi, considera **sotto-agenti** specializzati con i propri tool (Cap. 4).
- Tool con **nomi simili** confondono il modello. `search` vs `find` vs `lookup` → uno solo, ben definito.

## 6.7 Tool sicuri, tool pericolosi

I tool agiscono sul mondo. Categorie tipiche per pericolosità:

| Categoria | Esempi | Politica consigliata |
|---|---|---|
| **Read-only** | `read_file`, `web_search`, `query_db` | Lascia libero. |
| **Write reversibile** | `create_draft_email`, `add_to_cart` | Lascia libero ma logga. |
| **Write non reversibile** | `send_email`, `delete_file`, `charge_payment` | Conferma umana o whitelist. |
| **System-level** | `run_shell_command`, `exec_python` | Solo in sandbox isolato. |

Per i tool pericolosi, il pattern tipico è il **human-in-the-loop**: l'agente propone l'azione, mostra cosa farà, e aspetta conferma.

In Claude Code questo è gestito automaticamente: ogni Bash/Edit/Write chiede al utente l'autorizzazione, salvo permessi pre-approvati.

## 6.8 Tool che ritornano molto: troncamento e paginazione

Un tool che ritorna 5MB di output salura il context window. Best practice:

- **Tronca** output troppo lunghi (es. solo le prime 2000 righe).
- **Riassumi** se ha senso (un altro LLM può sintetizzare prima di rendere al primo).
- **Pagina** (cursor-based): il tool ritorna 50 risultati con un `next_cursor` per i successivi.
- **Filtra alla sorgente**: meglio `query_db(filters)` che torna 100 record giusti, che `list_all()` + filtraggio in chat.

Anche le **descrizioni dei limiti** vanno nel tool: "Ritorna max 50 risultati. Per più, usa il parametro `cursor`."

## 6.9 Errori dai tool

I tool falliscono. Il file non esiste, la rete cade, l'API ritorna 500. Devi decidere come gestirlo:

```python
def fetch_url(url: str) -> dict:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return {"ok": True, "content": r.text[:5000]}  # tronca
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

**Restituisci sempre un risultato strutturato**, anche per gli errori. Il modello sa leggere l'errore e ritentare con parametri diversi (es. URL corretto). Lanciare un'eccezione "rompe" l'agente.

## 6.10 MCP: il "USB-C" dei tool

**Model Context Protocol (MCP)** è uno standard aperto per servire tool a qualsiasi agente compatibile.

Idea: invece di re-implementare i tool per ogni agente, scrivi un **server MCP** che esporta tool, e qualsiasi client (Claude Code, Claude Desktop, Cursor) li può consumare.

Esempi di server MCP esistenti:
- `mcp-server-filesystem` — accesso file
- `mcp-server-github` — issue, PR, repo
- `mcp-server-postgres` — query a un Postgres
- `mcp-server-slack` — messaggi e canali

Vantaggi:
- Riusabilità tra client diversi.
- Separazione netta tra agente e tool.
- Ecosistema aperto (puoi pubblicare il tuo server).

Lo riprenderemo nei capitoli su Claude Code (Cap. 9) e su come costruire agenti (Cap. 10).

## 6.11 Pratica: progetta i tool per un agente "personal assistant"

Esercizio: immagina un agente che ti aiuta a gestire la giornata. Quali 6-8 tool gli daresti?

Una possibile risposta:

1. `read_calendar(date_range)` — legge gli appuntamenti.
2. `create_event(title, start, end, attendees)` — crea un appuntamento.
3. `search_emails(query)` — cerca nelle email.
4. `compose_email(to, subject, body, send=False)` — bozza/invio email (con flag).
5. `list_tasks(status)` — task aperte.
6. `add_task(title, due, priority)` — aggiunge task.
7. `web_search(query)` — info dal web.
8. `ask_user(question)` — chiede conferma in caso di ambiguità.

Nota:
- Email send con flag `send=False` di default: l'agente prepara, tu confermi.
- `ask_user` è un tool: dà al modello un modo *strutturato* per fare domande.
- Niente tool `do_anything`: scope chiaro.

## 6.12 Da ricordare

- **I tool sono ciò che rende l'LLM un agente.**
- **La descrizione del tool è il prompt più importante.** Spiegala come a un nuovo collega.
- **Schema preciso** dei parametri = meno errori del modello.
- **Pochi tool ben fatti** > tanti tool generici.
- **Per tool rischiosi**, human-in-the-loop o sandbox.
- **Errori strutturati** invece di eccezioni: il modello sa gestirli.
- **MCP** sta diventando lo standard per esporre tool tra agenti.

## 6.13 Errori tipici

- **Descrizioni vaghe.** "Tool per email" → il modello non sa quando usarlo.
- **Troppi tool simili.** Il modello sceglie a caso.
- **Tool con effetti collaterali nascosti.** "list_users" che in realtà invia anche un'email. Confonde l'agente e il debug.
- **Tool senza limiti di output.** Saturano il contesto e il portafoglio.
- **Eccezioni invece di errori strutturati.** Il modello non vede l'errore, solo che il loop si è rotto.
- **Lasciar tool pericolosi senza supervisione.** "L'agente ha cancellato la tabella di prod" non è una battuta.

---

I tool danno mani e occhi. La memoria dà *continuità nel tempo*. Vediamo come gestirla.

→ [Capitolo 7 — Memoria, contesto e RAG](07-memoria-contesto-e-rag.md)
