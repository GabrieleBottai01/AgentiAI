# 11. Framework: LangChain, AutoGen, CrewAI

I framework forniscono **astrazioni di alto livello** per costruire agenti senza scrivere il loop a mano. Ti danno: chiamate ai modelli unificate, tool pronti, memoria, multi-agente, observability.

Tradeoff classico: **velocità di sviluppo vs. controllo**. Bene da sapere quando scegliere quale, e quando *non* usare un framework.

## 11.1 Panoramica

| Framework | Focus | Punti di forza | Quando usarlo |
|---|---|---|---|
| **LangChain** | Composizione di chain e agent | Ecosistema enorme, integrazioni con tutto | Pipeline RAG, prototipi rapidi, dev che vogliono tool pronti |
| **LangGraph** | Workflow as graph | Controllo fine, stato esplicito, debug | Agenti complessi che richiedono branching, retry, human-in-the-loop |
| **AutoGen** | Multi-agente conversazionale | Pattern "agenti che parlano tra loro" | Simulazioni, debate, problemi che beneficiano di più ruoli |
| **CrewAI** | Multi-agente orientato a "team" | Astrazione "ruolo + task + tool" | Workflow business-like (ricerca → scrittura → editing) |
| **LiteLLM** | Adapter unificato per LLM | Uniforma l'API tra OpenAI, Anthropic, locale, ecc. | Quando vuoi provider-agnostic |
| **Pydantic AI** | Type-safe agents in Python | Rigore typing, validazione strutturata | Backend Python che valuta type-safety |
| **Vercel AI SDK** | Agent in TypeScript per app web | Streaming UI, hook React | Frontend/full-stack JS |

Non sono mutuamente esclusivi. Uno stack tipico potrebbe essere: `LiteLLM` (provider-agnostic) + `LangGraph` (orchestrazione) + `pgvector` (memoria) + `Langfuse` (observability).

## 11.2 LangChain: lo stato dell'arte (con riserve)

LangChain è il framework più popolare. Ha avuto un'evoluzione travagliata: la prima versione ("classic chains") è stata superata da una basata su **LCEL (LangChain Expression Language)** e poi affiancata da **LangGraph** per gli agent.

### Esempio: chain RAG con LangChain

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Vector store già popolato
vstore = Chroma(persist_directory="./db", embedding_function=OpenAIEmbeddings())
retriever = vstore.as_retriever(search_kwargs={"k": 4})

prompt = ChatPromptTemplate.from_template("""
Rispondi usando solo il contesto fornito.

Contesto: {context}

Domanda: {question}
""")

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | ChatAnthropic(model="claude-opus-4-7")
)

print(chain.invoke("Qual è la policy sui rimborsi viaggi?"))
```

**Pro:**
- 5 righe per RAG funzionante.
- Cambi modello cambiando 1 import.
- Ecosistema con centinaia di integrazioni (DB, API, vector store, parsers).

**Contro:**
- API instabile (breaking changes frequenti).
- "Magia" che nasconde problemi: quando qualcosa non va, debug è un viaggio.
- Astrazioni a volte forzate (LCEL può diventare poco leggibile).

**Verdetto:** ottimo per **prototipi** e per usare integrazioni che non vuoi reimplementare. Per agenti di produzione, preferisci **LangGraph** (sotto).

## 11.3 LangGraph: workflow as graph

LangGraph è il fratello "grown-up" di LangChain. L'agente si modella come un **grafo di nodi** dove ogni nodo è una funzione e gli archi sono transizioni condizionate.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    iterations: int

def call_model(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [response], "iterations": state["iterations"] + 1}

def call_tools(state: AgentState):
    last = state["messages"][-1]
    results = [execute_tool(call) for call in last.tool_calls]
    return {"messages": results}

def should_continue(state: AgentState):
    if state["iterations"] >= 10:
        return END
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", call_tools)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

app = graph.compile()
result = app.invoke({"messages": [...], "iterations": 0})
```

**Pro:**
- Stato esplicito → debug e replay facili.
- Branching condizionato, cicli, human-in-the-loop nativo.
- Persistenza dello stato tra run (checkpointing).
- Production-ready.

**Contro:**
- Curva di apprendimento più ripida.
- Overkill per task semplici.

**Quando usarlo:** agente complesso con più branch, retry, approvazioni umane, replay del workflow.

## 11.4 AutoGen: agenti che parlano tra loro

AutoGen (Microsoft Research) si focalizza su **conversational multi-agent**: definisci agenti con ruoli, falli dialogare, lascia emergere la soluzione.

```python
from autogen import AssistantAgent, UserProxyAgent

assistant = AssistantAgent(
    name="coder",
    llm_config={"config_list": [{"model": "gpt-5", "api_key": "..."}]},
    system_message="Sei un programmatore Python esperto."
)

reviewer = AssistantAgent(
    name="reviewer",
    llm_config={...},
    system_message="Sei un code reviewer rigoroso."
)

user = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "./tmp"}
)

user.initiate_chat(
    assistant,
    message="Scrivi una funzione che calcola Fibonacci con memoizzazione"
)
# poi reviewer commenta, coder rivede, user esegue, ecc.
```

**Pro:**
- Pattern naturale per problemi che beneficiano di "più punti di vista".
- Gestione conversazione multi-agent gratis.
- Ottimo per simulazioni e debate.

**Contro:**
- Agenti che chiacchierano = molti token. Costo alto.
- Convergere a una risposta "buona" richiede tuning fine dei system prompt.
- Spesso un singolo agente con reflection fa lo stesso a 1/3 del costo.

**Quando usarlo:** simulazioni educational, generazione di dialoghi, problemi di team in cui i ruoli sono *davvero* distinti.

## 11.5 CrewAI: team di agenti task-driven

CrewAI usa la metafora del "team aziendale": definisci **agenti** (ruoli), **task** (cose da fare), **tool** (strumenti), e li componi in una **crew**.

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Senior Researcher",
    goal="Trovare informazioni accurate sul tema X",
    backstory="Sei una ricercatrice meticolosa con anni di esperienza...",
    tools=[web_search_tool, scrape_tool]
)

writer = Agent(
    role="Tech Writer",
    goal="Scrivere articoli chiari basati su ricerca solida",
    backstory="...",
    tools=[]
)

research_task = Task(
    description="Indaga gli sviluppi recenti in {topic}",
    expected_output="Lista puntata con 5-7 fatti chiave e fonti",
    agent=researcher
)

write_task = Task(
    description="Scrivi un articolo divulgativo basato sui risultati",
    expected_output="Articolo di 800 parole, tono chiaro",
    agent=writer,
    context=[research_task]   # passa output di research come context
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True
)

result = crew.kickoff(inputs={"topic": "agenti AI nel 2026"})
```

**Pro:**
- Astrazione mentale facile per chi non viene da ML.
- Buono per workflow lineari (research → write → review).
- Comunità attiva, molti template.

**Contro:**
- Magia che a volte produce risultati mediocri.
- Personalità prompt ("backstory") può diventare romanzata e sprecare token.
- Per task brevi, un singolo agent è più efficiente.

**Quando usarlo:** automazione di workflow business con passi chiari, prototipo di un "team AI" da mostrare a chi non programma.

## 11.6 LiteLLM: l'adapter universale

Non è un framework di agenti, ma un **wrapper unificato** per tutti i provider. Stessa API, modelli diversi:

```python
from litellm import completion

# Cambi solo "model"
r1 = completion(model="claude-opus-4-7", messages=[...])
r2 = completion(model="gpt-5", messages=[...])
r3 = completion(model="gemini/gemini-2-pro", messages=[...])
r4 = completion(model="ollama/llama4", messages=[...])  # locale!
```

Ti dà:
- Provider switching semplice.
- Routing fallback (se Anthropic è down, tenta OpenAI).
- Telemetry e cost tracking.
- Proxy server per centralizzare le chiamate da più servizi.

**Quando usarlo:** sempre che ti aspetti di provare più provider o vuoi ridurre il vendor lock-in.

## 11.7 Pydantic AI: type-safe agents

Da Pydantic (libreria di validazione Python più amata). Approccio: **definisci I/O con tipi Python**, il framework gestisce serializzazione/parsing.

```python
from pydantic_ai import Agent
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    city: str
    temperature_celsius: float
    conditions: str

agent = Agent(
    "claude-opus-4-7",
    result_type=WeatherResponse,
    system_prompt="Sei un agente meteo."
)

result = agent.run_sync("Che tempo fa a Roma?")
print(result.data.city)               # str
print(result.data.temperature_celsius) # float
```

**Pro:**
- Validazione automatica dell'output.
- Ottima esperienza developer in Python (autocomplete, mypy).
- Lightweight, zero magia.

**Contro:**
- Più giovane di LangChain, meno integrazioni.
- Multi-agent meno sviluppato.

**Quando usarlo:** backend Python dove il rigore typing conta (FastAPI, microservizi).

## 11.8 Vercel AI SDK: agent in TypeScript

Per app web (Next.js, Svelte, ecc.), il Vercel AI SDK è di fatto lo standard.

```ts
import { streamText, tool } from 'ai';
import { anthropic } from '@ai-sdk/anthropic';
import { z } from 'zod';

const result = await streamText({
  model: anthropic('claude-opus-4-7'),
  tools: {
    weather: tool({
      description: 'Get weather for a city',
      parameters: z.object({ city: z.string() }),
      execute: async ({ city }) => fetchWeather(city),
    }),
  },
  prompt: 'What is the weather in Rome?',
});
```

Ti dà streaming, tool, structured output, hook React (`useChat`, `useCompletion`). Per chat UI in app web, è la via più rapida.

## 11.9 Quando NON usare un framework

I framework hanno un costo: **complessità nascosta + dipendenze + lock-in**.

Considera di farne a meno se:

- Il tuo agente è semplice (1-2 tool, loop diretto). 100 righe di Python con SDK puro sono più chiare di 30 righe di LangChain.
- Sei in un contesto con vincoli stringenti di dipendenze (embedded, pacchetti minimal).
- Devi debuggare un comportamento sottile e la magia del framework rende tutto opaco.
- La tua azienda ha policy di sicurezza che impediscono dipendenze npm/pip non verificate.

**Regola pragmatica:** inizia con SDK puro. Quando ti accorgi di stare scrivendo per la terza volta lo stesso boilerplate (RAG, retry, multi-agent), è il momento di considerare un framework.

## 11.10 Confronto rapido: scegliere

```
Hai un workflow semplice? → SDK puro (Cap. 10).
Vuoi RAG rapido? → LangChain.
Agente complesso, branching, human-in-the-loop? → LangGraph.
Multi-agente conversazionale? → AutoGen.
Workflow business "team-style"? → CrewAI.
Backend type-safe Python? → Pydantic AI.
App web TS/JS? → Vercel AI SDK.
Vuoi cambiare provider? → LiteLLM ovunque.
Observability? → Langfuse o LangSmith (orthogonal a tutti).
```

## 11.11 Observability: il pezzo che non puoi saltare

Una volta in produzione, gli agenti si rompono in modi imprevedibili. Senza tracing strutturato sei cieco.

Strumenti che integrano i framework sopra:

- **Langfuse** (open-source, self-hostable). Traccia chain, agent, costi, errori.
- **LangSmith** (di LangChain Inc, hosted). Equivalente commerciale, integrazione perfetta con LangChain/LangGraph.
- **Helicone** (proxy + observability). Si infila tra te e l'API.

Ti permettono di:
- Vedere ogni call con prompt, output, token usati, latency.
- Replay di sessioni problematiche.
- A/B test su prompt.
- Alert su errori o costi anomali.

Spendere 1 ora a setupare observability all'inizio risparmia giorni di debug dopo.

## 11.12 Pratica: rifare l'agente del Cap. 10 in LangGraph

Esercizio: prendi l'agente di research del Cap. 10 e riscrivilo in LangGraph. Vedrai:
- Quanto codice "loop" sparisce.
- Quanto guadagni in observability (traccia ogni step).
- Quanto perdi in semplicità.

Confronta i due e decidi quale ti convince di più *per il tuo uso*.

## 11.13 Da ricordare

- **Inizia con SDK puro.** Capisci come funziona davvero.
- **LangChain** per prototipi e RAG, **LangGraph** per agent in produzione.
- **AutoGen / CrewAI** per multi-agente, ma valuta se serve davvero.
- **LiteLLM** ovunque per provider-switching.
- **Vercel AI SDK** per app web TS.
- **Observability** (Langfuse o simili) non è opzionale.

## 11.14 Errori tipici

- **Saltare l'SDK puro.** Senza capire i fondamenti, i framework diventano scatole nere magiche.
- **Adottare framework instabili in produzione.** LangChain ha breaking changes ogni 6 mesi.
- **Multi-agente perché "fa figo".** Un agente con reflection spesso supera un team di agenti chiacchieroni.
- **Niente observability.** "Funziona in locale" → in produzione esplode senza che capisci perché.
- **Non bloccare le versioni delle dipendenze.** Update automatico = sorprese sgradevoli.

---

Sai costruire e orchestrare agenti. Adesso parliamo di **come lavorarci bene**: pratiche, workflow, qualità del lavoro.

→ [Capitolo 12 — Best practice di sviluppo con agenti](12-best-practice-sviluppo-con-agenti.md)
