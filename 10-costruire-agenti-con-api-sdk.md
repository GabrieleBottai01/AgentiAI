# 10. Costruire agenti custom con API e SDK

Adesso si costruisce. In questo capitolo facciamo un agente da zero in Python, con prompt caching, tool, gestione errori e best practice. Alla fine avrai un template che potrai estendere per la maggior parte dei tuoi casi d'uso.

## 10.1 Setup

Useremo l'**Anthropic SDK** come SDK primario. Tutto si traduce con piccole differenze in OpenAI SDK; segneremo le differenze importanti.

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

(Su [console.anthropic.com](https://console.anthropic.com) crei un'API key. Stessa cosa per [platform.openai.com](https://platform.openai.com) per OpenAI.)

## 10.2 Hello, agent

Il livello "chiamata singola":

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Ciao, chi sei?"}
    ]
)

print(response.content[0].text)
```

Questo è un chatbot, non un agente — niente loop, niente tool. Costruiamo l'agente vero.

## 10.3 Un agente minimale, runnable

```python
"""
Agente minimo: ha 2 tool (calcolatrice + ora corrente),
loopa finché il modello non smette di chiamare tool.
"""

from anthropic import Anthropic
from datetime import datetime
import json

client = Anthropic()
MODEL = "claude-opus-4-7"

# 1. Definizione dei tool
TOOLS = [
    {
        "name": "calculator",
        "description": "Esegue un'espressione aritmetica Python. Usa SOLO per calcoli numerici (es. '2+2', '15 * 23 / 4'). Non per testo o codice generico.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Espressione aritmetica valida in Python"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "current_time",
        "description": "Restituisce data e ora correnti in formato ISO. Usa quando l'utente chiede 'che ore sono', 'che giorno è', o per timestamp.",
        "input_schema": {"type": "object", "properties": {}}
    }
]

# 2. Implementazione dei tool
def calculator(expression: str) -> str:
    try:
        # ATTENZIONE: eval è pericoloso. In produzione usare un parser sicuro.
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"errore: {e}"

def current_time() -> str:
    return datetime.now().isoformat()

TOOL_FUNCS = {
    "calculator": calculator,
    "current_time": current_time,
}

# 3. Il loop dell'agente
def run_agent(user_message: str, max_iterations: int = 10) -> str:
    messages = [{"role": "user", "content": user_message}]

    for step in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system="Sei un assistente preciso. Usa i tool quando servono. Risposte concise.",
            tools=TOOLS,
            messages=messages,
        )

        # Aggiorna la storia con la risposta
        messages.append({"role": "assistant", "content": response.content})

        # Se non ha chiamato tool, ha finito
        if response.stop_reason != "tool_use":
            # Trova il blocco di testo finale
            text_blocks = [b for b in response.content if b.type == "text"]
            return text_blocks[-1].text if text_blocks else "(nessuna risposta)"

        # Esegui i tool richiesti
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                func = TOOL_FUNCS.get(block.name)
                if not func:
                    result = f"errore: tool '{block.name}' non esiste"
                else:
                    result = func(**block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})

    return "Limite iterazioni raggiunto."


# Prova
if __name__ == "__main__":
    print(run_agent("Quanti minuti sono passati dalla mezzanotte fino ad adesso?"))
```

Esegui questo file. L'agente:
1. Vede la domanda.
2. Chiama `current_time()`.
3. Pensa: "ora ho l'ora corrente, devo calcolare i minuti dalla mezzanotte".
4. Chiama `calculator("...")` con l'espressione giusta.
5. Risponde.

Tre passi di LLM, due tool. **Questo è un agente**.

## 10.4 Prompt caching: il trucco da imparare subito

Quando il system prompt è grande (centinaia o migliaia di token), pagarli a ogni chiamata è uno spreco. Il **prompt caching** dell'API Anthropic permette di caricare il system prompt **una volta** e riutilizzarlo a costo ~10% per le chiamate successive (entro 5 minuti).

```python
response = client.messages.create(
    model=MODEL,
    max_tokens=2048,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,   # es. 8000 token
            "cache_control": {"type": "ephemeral"}  # ← cache!
        }
    ],
    tools=TOOLS,
    messages=messages,
)
```

Per agenti che fanno molti turni con lo stesso system prompt, è un risparmio enorme. **Sempre attivo** in produzione su qualsiasi system prompt non banale.

Dettagli:
- TTL: 5 minuti dall'ultima lettura. Si rinnova a ogni hit.
- Granularità: a blocchi. Puoi marcare il system prompt come cached e i tool come non cached.
- I tool definitions possono anch'essi essere cachati.

OpenAI ha un meccanismo equivalente automatico (cache hit dopo i primi 1024 token comuni).

## 10.5 Streaming

Per UX migliore, attiva lo streaming. Il modello ritorna i token man mano che li produce.

```python
with client.messages.stream(
    model=MODEL,
    max_tokens=2048,
    messages=[{"role": "user", "content": "Spiegami le reti neurali"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    print()
```

In agenti con tool, lo streaming si gestisce con event-based handlers (più complesso, ma utile per dare feedback realtime all'utente).

## 10.6 Structured outputs (JSON mode)

Se vuoi che il modello risponda in JSON conforme a uno schema, usa il pattern "tool con un solo tool" o le feature dedicate.

OpenAI ha `response_format={"type": "json_schema", "json_schema": {...}}`, garantisce JSON valido.

Anthropic non ha ancora un mode strict ma il pattern del "tool unico" è equivalente:

```python
extract_tool = {
    "name": "extract_person",
    "description": "Estrae info su una persona dal testo.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "occupation": {"type": "string"}
        },
        "required": ["name"]
    }
}

response = client.messages.create(
    model=MODEL,
    max_tokens=1024,
    tools=[extract_tool],
    tool_choice={"type": "tool", "name": "extract_person"},  # ← forza l'uso
    messages=[{"role": "user", "content": "Mario, 42 anni, ingegnere..."}]
)

extracted = response.content[0].input  # già dict valido
```

`tool_choice` forzato garantisce che il modello chiami quel tool, e i parametri sono validati contro lo schema.

## 10.7 Retry, timeout, errori

In produzione la rete cade, le API ritornano 429 (rate limit) o 503. Best practice:

```python
from anthropic import APIError, APIConnectionError, RateLimitError
import time

def call_with_retry(fn, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return fn()
        except RateLimitError:
            wait = 2 ** attempt
            print(f"rate limit, retry tra {wait}s")
            time.sleep(wait)
        except APIConnectionError:
            time.sleep(1)
        except APIError as e:
            if e.status_code >= 500 and attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                raise
    raise RuntimeError("max retry raggiunti")
```

Configurazioni utili al client:

```python
client = Anthropic(
    timeout=30.0,
    max_retries=3,    # SDK ha già retry esponenziale built-in
)
```

## 10.8 Loop infiniti: come prevenirli

Tre protezioni standard:

1. **Limite di iterazioni**: già visto, mai oltre 25-30.
2. **Limite di token cumulativi**: traccia il totale, fermati a soglia.
3. **Detection di loop**: se l'agente chiama lo stesso tool con gli stessi argomenti 3 volte, fermati e logga.

```python
seen_calls = set()
for block in response.content:
    if block.type == "tool_use":
        signature = (block.name, json.dumps(block.input, sort_keys=True))
        if signature in seen_calls:
            return "Loop rilevato, fermo l'agente."
        seen_calls.add(signature)
```

## 10.9 OpenAI SDK: differenze chiave

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "...",
            "parameters": {...}  # JSON Schema
        }
    }]
)

# Risultato accessibile a:
# response.choices[0].message.tool_calls
# response.choices[0].finish_reason  ('tool_calls', 'stop', ...)
```

Differenze rispetto ad Anthropic:
- Tool wrappato in `{"type": "function", "function": {...}}`.
- `parameters` invece di `input_schema`.
- Risposta in `choices[0].message.tool_calls` (lista di tool calls).
- `tool_call.function.arguments` è una stringa JSON, va parsato.
- Tool result va come messaggio role=`"tool"` con `tool_call_id`.

Se vuoi codice agnostico, usa **LiteLLM** (Cap. 11) che astrae le differenze.

## 10.10 Claude Agent SDK

Per agenti complessi con harness simile a Claude Code (file ops, bash, todo, MCP), Anthropic offre il **Claude Agent SDK**:

```python
from claude_agent_sdk import ClaudeAgent

agent = ClaudeAgent(
    system_prompt="Sei un agente sviluppatore.",
    allowed_tools=["read_file", "write_file", "bash"],
    working_directory="./my-project"
)

result = await agent.run("Aggiungi un endpoint /health all'app FastAPI")
```

Ti dà gratis: gestione filesystem, esecuzione comandi, prompt caching, compaction automatica. Vale la pena per coding agents seri.

## 10.11 Costi: capire e ottimizzare

I costi si calcolano sui token (input + output). Tariffe tipiche 2026 (varia, controlla sempre):

| Modello | Input ($/M tok) | Output ($/M tok) |
|---|---|---|
| Claude Opus 4.7 | ~15 | ~75 |
| Claude Sonnet 4.6 | ~3 | ~15 |
| Claude Haiku 4.5 | ~0.80 | ~4 |
| GPT-5 | ~10 | ~40 |
| GPT-5 Mini | ~0.25 | ~2 |

Trick per risparmiare:

1. **Prompt caching** sul system prompt → -90% sull'input ripetuto.
2. **Modelli piccoli** dove bastano. Spesso Haiku/Mini fanno l'80% dei task per il 5% del costo.
3. **Tronca i tool result** a quello che serve davvero.
4. **Compaction** della history quando lunga.
5. **Batch API** per task non realtime → -50%.
6. **Cap di iterazioni e token** per impedire loop costosi.

Setta SEMPRE un **budget alert** sull'API console quando metti in produzione.

## 10.12 Esempio finale: agente di research

Mettiamo insieme tutto in un agente che cerca nel web e produce un brief.

```python
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic

client = Anthropic()

def web_search(query: str) -> str:
    """Fake: in realtà chiamerebbe SerpAPI / Tavily / Brave Search API."""
    return f"[risultati per: {query}]"

def fetch_url(url: str) -> dict:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)[:5000]
        return {"ok": True, "content": text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

TOOLS = [
    {
        "name": "web_search",
        "description": "Cerca nel web. Usa per fatti aggiornati o ricerche generali.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "fetch_url",
        "description": "Scarica e estrae testo da una URL. Usa per leggere fonti specifiche.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"]
        }
    }
]

TOOL_FUNCS = {"web_search": web_search, "fetch_url": fetch_url}

SYSTEM = """Sei un agente di ricerca. Procedura:
1. Comprendi la domanda. Se ambigua, fai un'unica domanda chiarificatrice nel testo.
2. Fai 1-3 ricerche web mirate.
3. Per le 2-3 fonti più promettenti, leggile con fetch_url.
4. Sintetizza un brief di 200-300 parole CITANDO le fonti.
5. Se le info non bastano, dillo invece di inventare.

Stop quando hai un brief soddisfacente."""

def research(question: str, max_iters: int = 15) -> str:
    messages = [{"role": "user", "content": question}]
    for step in range(max_iters):
        resp = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            system=[{"type": "text", "text": SYSTEM, "cache_control": {"type": "ephemeral"}}],
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return next(b.text for b in resp.content if b.type == "text")
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out = TOOL_FUNCS[b.name](**b.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": b.id,
                    "content": str(out),
                })
        messages.append({"role": "user", "content": results})
    return "Iterazioni esaurite."

print(research("Qual è lo stato dei modelli AI open-source nel 2026?"))
```

200 righe, un agente di research vero. Da qui aggiungi: persistenza della history, retry, observability (Langfuse/LangSmith), web search vera (SerpAPI o Tavily).

## 10.13 Da ricordare

- **Il loop è ~50 righe.** Tutto il valore sta nei tool e nei prompt.
- **Prompt caching** per system prompt grandi: risparmio enorme.
- **Limite iterazioni + detection di loop** per non andare in spirale.
- **Tool result strutturato (ok/error)** per far recuperare l'agente.
- **Streaming** per UX, **tool_choice forzato** per output strutturato.
- **Modello piccolo dove basta**, modello grosso solo dove serve.
- **Budget alert** in produzione, sempre.

## 10.14 Errori tipici

- **Niente cache**: paghi 10x il dovuto su system prompt grandi.
- **Niente limite iterazioni**: una notte ti accorgi di aver bruciato 50€.
- **Tool che ritorna 100KB di HTML**: contesto saturato, costi che esplodono.
- **Eccezioni nei tool** invece di error string strutturato: l'agente si rompe.
- **`eval` come calcolatrice**: in produzione apre buchi di sicurezza enormi.
- **Lasciare il modello "Opus" sempre**: prova Sonnet/Haiku, spesso vanno bene.

---

Costruire da zero è educativo e flessibile. Per pipeline più complesse, i framework danno un'astrazione più alta. Vediamo i principali.

→ [Capitolo 11 — Framework: LangChain, AutoGen, CrewAI](11-framework-langchain-autogen-crewai.md)
