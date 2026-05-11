"""
Sito della Guida agli Agenti AI.

Architettura:
- FastAPI con Jinja2 (server-side rendering).
- I capitoli sono i file .md della guida.
- L'utente inserisce la propria API key nel browser; ogni chiamata AI
  passa la key via header e il backend la usa per chiamare Anthropic
  senza loggarla né persisterla.
- Streaming SSE per chat e playground.

Avvio:
    cd site
    python3 main.py
    # apri http://localhost:8000
"""

import json
import re
from pathlib import Path
from typing import AsyncIterator, Optional

import httpx
import markdown
from anthropic import AsyncAnthropic
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
GUIDE_DIR = ROOT.parent
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))

app = FastAPI(title="Guida agli Agenti AI")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

# ----------------------------------------------------------------------------
# Chapter loading
# ----------------------------------------------------------------------------
CHAPTERS = [
    {"n": 1, "slug": "01-cosa-sono-gli-agenti-ai", "title": "Cosa sono gli Agenti AI", "part": "Parte 1 — Fondamenti"},
    {"n": 2, "slug": "02-come-funzionano-gli-llm", "title": "Come funzionano gli LLM", "part": "Parte 1 — Fondamenti"},
    {"n": 3, "slug": "03-anatomia-di-un-agente", "title": "Anatomia di un agente", "part": "Parte 1 — Fondamenti"},
    {"n": 4, "slug": "04-tipi-di-agenti-e-architetture", "title": "Tipi di agenti e architetture", "part": "Parte 1 — Fondamenti"},
    {"n": 5, "slug": "05-prompt-engineering", "title": "Prompt engineering", "part": "Parte 2 — Tecniche"},
    {"n": 6, "slug": "06-tool-use-e-function-calling", "title": "Tool use e function calling", "part": "Parte 2 — Tecniche"},
    {"n": 7, "slug": "07-memoria-contesto-e-rag", "title": "Memoria, contesto e RAG", "part": "Parte 2 — Tecniche"},
    {"n": 8, "slug": "08-usare-i-chatbot-ai", "title": "Usare i chatbot AI", "part": "Parte 3 — Usare gli agenti"},
    {"n": 9, "slug": "09-claude-code-per-sviluppatori", "title": "Claude Code per sviluppatori", "part": "Parte 3 — Usare gli agenti"},
    {"n": 10, "slug": "10-costruire-agenti-con-api-sdk", "title": "Costruire agenti con API e SDK", "part": "Parte 4 — Costruire"},
    {"n": 11, "slug": "11-framework-langchain-autogen-crewai", "title": "Framework: LangChain, AutoGen, CrewAI", "part": "Parte 4 — Costruire"},
    {"n": 12, "slug": "12-best-practice-sviluppo-con-agenti", "title": "Best practice di sviluppo", "part": "Parte 5 — Lavorare bene"},
    {"n": 13, "slug": "13-sicurezza-costi-e-limiti", "title": "Sicurezza, costi, limiti", "part": "Parte 5 — Lavorare bene"},
    {"n": 14, "slug": "14-valutazione-e-miglioramento", "title": "Valutazione e miglioramento", "part": "Parte 5 — Lavorare bene"},
    {"n": 15, "slug": "15-casi-uso-e-workflow-reali", "title": "Casi d'uso e workflow reali", "part": "Parte 6 — Applicazioni"},
    {"n": 16, "slug": "16-glossario-e-risorse", "title": "Glossario e risorse", "part": "Parte 6 — Applicazioni"},
]
CHAPTER_BY_SLUG = {c["slug"]: c for c in CHAPTERS}
CHAPTER_BY_N = {c["n"]: c for c in CHAPTERS}

# Esercizi pre-configurati per capitolo: rendered come widget interattivi.
EXERCISES = {
    1: {
        "id": "ex-cap1",
        "type": "classify",
        "title": "Esercizio: agente o chatbot?",
        "intro": "Per ognuna delle descrizioni, decidi se è un <b>agente</b>, un <b>chatbot</b> o un'<b>automazione con AI</b>. Poi premi 'Verifica' per il giudizio del tutor AI.",
        "cases": [
            "Un assistente che, dato un bug report, esplora il codebase, propone una fix, scrive i test e apre la PR.",
            "Un'integrazione che traduce automaticamente i messaggi quando ne arriva uno in lingua diversa.",
            "Un copilota che risponde a domande sulla cucina italiana e suggerisce ricette.",
        ],
    },
    5: {
        "id": "ex-cap5",
        "type": "improve_prompt",
        "title": "Esercizio: migliora questo prompt",
        "intro": "Il prompt qui sotto è generico. Riscrivilo seguendo i criteri del capitolo (ruolo, obiettivo, vincoli, formato, esempi). Poi premi 'Valuta' per ricevere il feedback dell'AI.",
        "starter": "Riassumi il testo che ti mando.",
    },
    6: {
        "id": "ex-cap6",
        "type": "design_tool",
        "title": "Esercizio: progetta un tool",
        "intro": "Immagina un agente che prenota voli. Scrivi la <b>definizione di un tool</b> (nome, descrizione, schema parametri) seguendo le linee guida del capitolo. L'AI valuterà chiarezza, precisione e robustezza dello schema.",
        "starter": '{\n  "name": "search_flights",\n  "description": "...",\n  "input_schema": {\n    "type": "object",\n    "properties": {\n      ...\n    },\n    "required": [...]\n  }\n}',
    },
}

CHAPTER_CACHE: dict[str, str] = {}


def _md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "sane_lists", "nl2br", "codehilite", "toc"],
        extension_configs={
            "codehilite": {"css_class": "codehilite", "guess_lang": False},
            "toc": {"permalink": False},
        },
    )


def get_chapter_html(slug: str) -> Optional[str]:
    if slug in CHAPTER_CACHE:
        return CHAPTER_CACHE[slug]
    path = GUIDE_DIR / f"{slug}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    # Rimuovi frecce di navigazione finali (sostituiti dal nostro layout)
    text = re.sub(r"\n→ \[.*?\]\(.*?\)\s*$", "", text, flags=re.DOTALL)
    text = re.sub(r"\n← \[.*?\]\(.*?\)\s*$", "", text, flags=re.DOTALL)
    html = _md_to_html(text)
    CHAPTER_CACHE[slug] = html
    return html


# ----------------------------------------------------------------------------
# Routes — pagine
# ----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return TEMPLATES.TemplateResponse(
        "index.html",
        {"request": request, "chapters": CHAPTERS, "active": "home"},
    )


@app.get("/capitolo/{slug}", response_class=HTMLResponse)
async def chapter(request: Request, slug: str):
    chapter = CHAPTER_BY_SLUG.get(slug)
    if not chapter:
        raise HTTPException(404, "Capitolo non trovato")
    html = get_chapter_html(slug)
    if html is None:
        raise HTTPException(404, "Contenuto non trovato")

    idx = next(i for i, c in enumerate(CHAPTERS) if c["slug"] == slug)
    prev_ch = CHAPTERS[idx - 1] if idx > 0 else None
    next_ch = CHAPTERS[idx + 1] if idx < len(CHAPTERS) - 1 else None

    return TEMPLATES.TemplateResponse(
        "chapter.html",
        {
            "request": request,
            "chapters": CHAPTERS,
            "chapter": chapter,
            "content": html,
            "prev_ch": prev_ch,
            "next_ch": next_ch,
            "exercise": EXERCISES.get(chapter["n"]),
            "active": "chapters",
        },
    )


@app.get("/Guida-Agenti-AI.pdf")
async def download_pdf():
    pdf = GUIDE_DIR / "Guida-Agenti-AI.pdf"
    if not pdf.exists():
        raise HTTPException(404, "PDF non disponibile")
    return FileResponse(str(pdf), media_type="application/pdf", filename="Guida-Agenti-AI.pdf")


@app.get("/capitolo/n/{n}")
async def chapter_by_number(n: int):
    ch = CHAPTER_BY_N.get(n)
    if not ch:
        raise HTTPException(404)
    return RedirectResponse(f"/capitolo/{ch['slug']}")


@app.get("/playground", response_class=HTMLResponse)
async def playground(request: Request):
    return TEMPLATES.TemplateResponse(
        "playground.html",
        {"request": request, "chapters": CHAPTERS, "active": "playground"},
    )


@app.get("/agente-demo", response_class=HTMLResponse)
async def agent_demo(request: Request):
    return TEMPLATES.TemplateResponse(
        "agent.html",
        {"request": request, "chapters": CHAPTERS, "active": "agent"},
    )


@app.get("/tutor", response_class=HTMLResponse)
async def tutor(request: Request):
    return TEMPLATES.TemplateResponse(
        "tutor.html",
        {"request": request, "chapters": CHAPTERS, "active": "tutor"},
    )


# ----------------------------------------------------------------------------
# API helpers
# ----------------------------------------------------------------------------
def _get_api_key(x_anthropic_key: Optional[str]) -> str:
    if not x_anthropic_key or not x_anthropic_key.startswith("sk-ant-"):
        raise HTTPException(
            401,
            "API key Anthropic mancante o non valida. Inseriscila in alto a destra (deve iniziare con sk-ant-).",
        )
    return x_anthropic_key


def _client(api_key: str) -> AsyncAnthropic:
    return AsyncAnthropic(api_key=api_key)


# ----------------------------------------------------------------------------
# API — chat tutor (streaming SSE)
# ----------------------------------------------------------------------------
class ChatMessage(BaseModel):
    role: str
    content: str


class TutorRequest(BaseModel):
    messages: list[ChatMessage]
    chapter_slug: Optional[str] = None
    model: str = "claude-haiku-4-5"


TUTOR_SYSTEM = """Sei il tutor AI della "Guida agli Agenti AI" di Gabriele Bottai.

Il tuo compito: aiutare gli utenti a capire i concetti della guida con spiegazioni chiare, esempi concreti, analogie semplici. Quando l'utente chiede qualcosa di non coperto, comunque rispondi se è pertinente al tema "agenti AI / LLM / sviluppo con AI".

Stile:
- Italiano, tono diretto e amichevole.
- Risposte concise (4-8 frasi tipiche). Solo quando serve, più lunghe.
- Esempi pratici prima dei termini astratti.
- Se citi un capitolo, usa il formato "(vedi Cap. N)".
- Se la domanda è ambigua, fai UNA domanda chiarificatrice prima di rispondere.

Capitoli della guida:
1. Cosa sono gli Agenti AI — definizione, agente vs chatbot
2. Come funzionano gli LLM — token, contesto, sampling
3. Anatomia di un agente — loop, tool, memoria, orchestratore
4. Tipi di agenti — ReAct, Plan-Execute, multi-agent
5. Prompt engineering — struttura, few-shot, CoT, output strutturato
6. Tool use e function calling — schema, descrizioni, sicurezza
7. Memoria, contesto e RAG — embedding, vector store, chunking
8. Usare i chatbot — ChatGPT, Claude.ai, Gemini, workflow
9. Claude Code — CLI agente, slash commands, hooks, MCP
10. Costruire con SDK — Anthropic SDK, prompt caching, loop
11. Framework — LangChain, LangGraph, AutoGen, CrewAI
12. Best practice — eval set, prompt versionati, human-in-the-loop
13. Sicurezza, costi, limiti — prompt injection, sandbox, GDPR
14. Valutazione — eval suite, metriche, A/B test
15. Casi d'uso — coding, support, ricerca, scrittura
16. Glossario e risorse"""


@app.post("/api/tutor")
async def api_tutor(
    body: TutorRequest,
    x_anthropic_key: Optional[str] = Header(None, alias="X-Anthropic-Key"),
):
    api_key = _get_api_key(x_anthropic_key)
    client = _client(api_key)

    # Aggiungi contesto del capitolo se fornito
    system_prompt = TUTOR_SYSTEM
    if body.chapter_slug:
        ch = CHAPTER_BY_SLUG.get(body.chapter_slug)
        if ch:
            system_prompt += f"\n\nL'utente sta leggendo il Capitolo {ch['n']}: {ch['title']}. Tieni conto del contesto."

    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    async def stream() -> AsyncIterator[bytes]:
        try:
            async with client.messages.stream(
                model=body.model,
                max_tokens=2048,
                system=system_prompt,
                messages=messages,
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'delta': text})}\n\n".encode()
            yield b"data: {\"done\": true}\n\n"
        except Exception as e:
            err = {"error": str(e)}
            yield f"data: {json.dumps(err)}\n\n".encode()

    return StreamingResponse(stream(), media_type="text/event-stream")


# ----------------------------------------------------------------------------
# API — playground (system + user → streaming)
# ----------------------------------------------------------------------------
class PlaygroundRequest(BaseModel):
    system: str = ""
    user: str
    model: str = "claude-haiku-4-5"
    temperature: float = 0.7
    max_tokens: int = 1024


@app.post("/api/playground")
async def api_playground(
    body: PlaygroundRequest,
    x_anthropic_key: Optional[str] = Header(None, alias="X-Anthropic-Key"),
):
    api_key = _get_api_key(x_anthropic_key)
    client = _client(api_key)

    system = body.system.strip() or "Sei un assistente utile."

    async def stream() -> AsyncIterator[bytes]:
        try:
            async with client.messages.stream(
                model=body.model,
                max_tokens=body.max_tokens,
                temperature=body.temperature,
                system=system,
                messages=[{"role": "user", "content": body.user}],
            ) as s:
                in_tokens = 0
                out_tokens = 0
                async for ev in s:
                    if ev.type == "text":
                        yield f"data: {json.dumps({'delta': ev.text})}\n\n".encode()
                final = await s.get_final_message()
                in_tokens = final.usage.input_tokens
                out_tokens = final.usage.output_tokens
                meta = {"done": True, "input_tokens": in_tokens, "output_tokens": out_tokens}
                yield f"data: {json.dumps(meta)}\n\n".encode()
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n".encode()

    return StreamingResponse(stream(), media_type="text/event-stream")


# ----------------------------------------------------------------------------
# API — demo agente con tool use (loop visibile)
# ----------------------------------------------------------------------------
class AgentRequest(BaseModel):
    goal: str
    model: str = "claude-haiku-4-5"
    max_iterations: int = 8


# Tool simulati: l'agente li chiama e noi rispondiamo con dati realistici
AGENT_TOOLS = [
    {
        "name": "calculator",
        "description": "Esegue espressioni aritmetiche Python (es. '2+2', '15*23/4'). Usa SOLO per calcoli numerici.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "current_time",
        "description": "Restituisce data e ora correnti in formato ISO-8601. Usa per timestamp o per calcolare durate.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "web_search",
        "description": "Cerca nel web. Restituisce 3-5 snippet rilevanti. Usa per fatti aggiornati o ricerche generali.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "fetch_url",
        "description": "Scarica e estrae testo da una URL. Usa SOLO se hai un URL specifico (preferibilmente da web_search).",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
]


def _exec_calculator(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"errore: {e}"


def _exec_current_time() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


async def _exec_web_search(query: str) -> str:
    """Demo search: usa DuckDuckGo Instant Answer API (gratuita, no key)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            r = await http.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            )
            data = r.json()
            results = []
            if data.get("AbstractText"):
                results.append(f"- {data['AbstractText']} (fonte: {data.get('AbstractURL', 'DuckDuckGo')})")
            for topic in data.get("RelatedTopics", [])[:4]:
                if isinstance(topic, dict) and topic.get("Text"):
                    url = topic.get("FirstURL", "")
                    results.append(f"- {topic['Text']} ({url})")
            if not results:
                return f"(Nessun risultato strutturato per '{query}'. La query potrebbe essere troppo specifica.)"
            return "\n".join(results)
    except Exception as e:
        return f"errore di rete: {e}"


async def _exec_fetch_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as http:
            r = await http.get(url, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            text = r.text
            # Strip HTML rudimentale
            from html.parser import HTMLParser

            class TextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.parts = []
                    self.skip = False

                def handle_starttag(self, tag, attrs):
                    if tag in ("script", "style"):
                        self.skip = True

                def handle_endtag(self, tag):
                    if tag in ("script", "style"):
                        self.skip = False

                def handle_data(self, data):
                    if not self.skip:
                        s = data.strip()
                        if s:
                            self.parts.append(s)

            ex = TextExtractor()
            ex.feed(text)
            extracted = " ".join(ex.parts)[:3000]
            return extracted or "(pagina vuota o non testuale)"
    except Exception as e:
        return f"errore: {e}"


@app.post("/api/agent")
async def api_agent(
    body: AgentRequest,
    x_anthropic_key: Optional[str] = Header(None, alias="X-Anthropic-Key"),
):
    api_key = _get_api_key(x_anthropic_key)
    client = _client(api_key)

    system = """Sei un agente di ricerca e assistenza. Hai a disposizione 4 tool:
- calculator: per qualsiasi calcolo numerico.
- current_time: per data/ora correnti.
- web_search: per cercare nel web.
- fetch_url: per leggere una pagina specifica.

Procedura: capisci l'obiettivo, usa i tool quando servono, sintetizza una risposta finale concisa (3-6 frasi) citando le fonti se hai cercato nel web.
Se dopo qualche tentativo non hai abbastanza info, dillo invece di inventare. Massimo 8 iterazioni."""

    messages = [{"role": "user", "content": body.goal}]

    async def stream() -> AsyncIterator[bytes]:
        try:
            for step in range(body.max_iterations):
                yield f"data: {json.dumps({'type': 'thinking', 'step': step + 1})}\n\n".encode()
                response = await client.messages.create(
                    model=body.model,
                    max_tokens=2048,
                    system=system,
                    tools=AGENT_TOOLS,
                    messages=messages,
                )

                # Aggiungi assistant message alla storia
                messages.append({"role": "assistant", "content": response.content})

                # Estrai eventuale testo intermedio
                for block in response.content:
                    if block.type == "text" and block.text.strip():
                        yield f"data: {json.dumps({'type': 'text', 'content': block.text})}\n\n".encode()

                if response.stop_reason != "tool_use":
                    yield f"data: {json.dumps({'type': 'done', 'stop_reason': response.stop_reason})}\n\n".encode()
                    return

                # Esegui i tool
                tool_results = []
                for block in response.content:
                    if block.type != "tool_use":
                        continue
                    tool_name = block.name
                    tool_input = block.input
                    yield f"data: {json.dumps({'type': 'tool_call', 'name': tool_name, 'input': tool_input})}\n\n".encode()

                    if tool_name == "calculator":
                        result = _exec_calculator(tool_input.get("expression", ""))
                    elif tool_name == "current_time":
                        result = _exec_current_time()
                    elif tool_name == "web_search":
                        result = await _exec_web_search(tool_input.get("query", ""))
                    elif tool_name == "fetch_url":
                        result = await _exec_fetch_url(tool_input.get("url", ""))
                    else:
                        result = f"errore: tool sconosciuto '{tool_name}'"

                    yield f"data: {json.dumps({'type': 'tool_result', 'name': tool_name, 'result': result[:1500]})}\n\n".encode()

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result[:5000],
                    })

                messages.append({"role": "user", "content": tool_results})

            yield f"data: {json.dumps({'type': 'done', 'stop_reason': 'max_iterations'})}\n\n".encode()
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n".encode()

    return StreamingResponse(stream(), media_type="text/event-stream")


# ----------------------------------------------------------------------------
# API — esercizi (validati da AI)
# ----------------------------------------------------------------------------
class ExerciseSubmit(BaseModel):
    exercise_id: str
    answers: dict
    model: str = "claude-haiku-4-5"


EXERCISE_PROMPTS = {
    "ex-cap1": """Sei il tutor della guida. Valuta le risposte dello studente all'esercizio sul Capitolo 1 (agente vs chatbot vs automazione).

Le 3 descrizioni e la risposta corretta:
1. Bug-fix autonomo con esplorazione e PR → AGENTE (loop, decisione, tool)
2. Traduzione automatica messaggi → AUTOMAZIONE (singolo passo, no loop)
3. Q&A su cucina → CHATBOT (no tool, no loop)

Risposte dello studente (JSON con chiavi item-0, item-1, item-2):
{ANSWERS}

Per ogni risposta:
- Indica se è giusta o sbagliata.
- Spiega in 1-2 frasi PERCHÉ, citando i criteri "loop" / "decisione autonoma" / "tool".
Conclusione finale: punteggio X/3 e un consiglio.""",

    "ex-cap5": """Sei un esperto di prompt engineering. Lo studente ha riscritto il prompt "Riassumi il testo che ti mando." in qualcosa di più strutturato. Valuta secondo i criteri del Capitolo 5: ruolo, obiettivo, contesto, vincoli, formato dell'output, esempi.

Prompt dello studente:
\"\"\"
{PROMPT}
\"\"\"

Restituisci:
1. Cosa funziona (2-3 punti specifici).
2. Cosa manca o si potrebbe migliorare (con esempi concreti).
3. Voto da 1 a 10 con giustificazione in una frase.
4. Una versione migliorata di esempio (massimo 8 righe).""",

    "ex-cap6": """Sei un esperto di tool design per agenti AI. Lo studente ha progettato la definizione di un tool per cercare voli. Valuta secondo i criteri del Capitolo 6: chiarezza della description, precisione dello schema dei parametri, gestione casi d'uso e non, robustezza.

Tool dello studente:
\"\"\"
{TOOL_DEF}
\"\"\"

Restituisci:
1. Validità sintattica (è JSON valido? lo schema è corretto?).
2. Qualità della description: il modello capirebbe quando usarlo? Cita criteri specifici.
3. Qualità dei parametri: tipi, descrizioni, required, enum dove utili.
4. Voto 1-10 con motivazione.
5. Una versione rivista di esempio (formattata, max 25 righe).""",
}


@app.post("/api/exercise")
async def api_exercise(
    body: ExerciseSubmit,
    x_anthropic_key: Optional[str] = Header(None, alias="X-Anthropic-Key"),
):
    api_key = _get_api_key(x_anthropic_key)
    client = _client(api_key)

    template = EXERCISE_PROMPTS.get(body.exercise_id)
    if not template:
        raise HTTPException(404, f"Esercizio {body.exercise_id} non trovato")

    if body.exercise_id == "ex-cap1":
        prompt = template.replace("{ANSWERS}", json.dumps(body.answers, ensure_ascii=False, indent=2))
    elif body.exercise_id == "ex-cap5":
        prompt = template.replace("{PROMPT}", body.answers.get("prompt", ""))
    elif body.exercise_id == "ex-cap6":
        prompt = template.replace("{TOOL_DEF}", body.answers.get("tool_def", ""))
    else:
        prompt = template

    async def stream() -> AsyncIterator[bytes]:
        try:
            async with client.messages.stream(
                model=body.model,
                max_tokens=2048,
                system="Sei un tutor preciso, costruttivo, in italiano. Usa formattazione markdown leggera.",
                messages=[{"role": "user", "content": prompt}],
            ) as s:
                async for text in s.text_stream:
                    yield f"data: {json.dumps({'delta': text})}\n\n".encode()
            yield b"data: {\"done\": true}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n".encode()

    return StreamingResponse(stream(), media_type="text/event-stream")


# ----------------------------------------------------------------------------
# Entrypoint
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
