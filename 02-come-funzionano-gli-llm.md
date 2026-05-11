# 2. Come funzionano gli LLM (il motore)

Per usare bene un agente devi sapere cosa succede *dentro* il suo motore — l'LLM. Non serve la matematica, serve l'**intuizione giusta**.

## 2.1 Cosa fa, in una frase, un LLM

> Dato un testo, predice il pezzo di testo successivo più probabile.

Tutto qui. Letteralmente. Un modello come GPT-5, Claude 4 o Gemini 2 ha una sola super-abilità: dato un input, prevedere cosa viene dopo.

```
Input:  "Il sole sorge a..."
Modello: predice "est"
```

Quando ti sembra che "ragioni", "scriva poesie", "spieghi codice", in realtà sta sempre facendo la stessa cosa: predicendo i token successivi, uno alla volta, con una probabilità calcolata.

La magia è che, allenato su miliardi di documenti, il pattern "qual è la prossima parola plausibile" copre quasi tutto: traduzione, sintesi, ragionamento, codice. Non perché capisca davvero, ma perché ha visto tantissimi esempi di "come continua un testo che inizia così".

## 2.2 I token: la valuta degli LLM

Un LLM non lavora con caratteri o parole, ma con **token**. Un token è un pezzo di testo, di solito 3-4 caratteri o una parola corta.

```
"Ciao, come stai?"  →  ["Ciao", ",", " come", " stai", "?"]   (5 token)
"Buongiornissimo"   →  ["Buon", "giorni", "ssimo"]            (3 token)
```

Perché ti interessa?

1. **Tutto si misura in token.** I costi delle API si calcolano in token (input + output). Il "context window" di un modello si misura in token.
2. **Token ≠ parole.** Un testo italiano "occupa" più token di un testo inglese a parità di parole, perché i tokenizer sono ottimizzati sull'inglese. Regola spannometrica: 1 parola italiana ≈ 1.5-2 token.
3. **Il modello vede solo i token.** Se cambi anche una virgola, l'input cambia. Nei prompt-engineering trick (Cap. 5) questo conta.

Strumento pratico: il [tokenizer di OpenAI](https://platform.openai.com/tokenizer) ti mostra come un testo viene "spezzato" in token.

## 2.3 Il context window

Il **context window** è la quantità massima di token che il modello può "vedere" in un singolo turno: input + output insieme.

Numeri tipici nel 2026:
- Claude 4.7 Opus: **1M di token** (≈ 750.000 parole, ovvero circa due copie di *Guerra e pace*).
- GPT-5: ordine dei 200K-400K token a seconda del piano.
- Gemini 2: fino a 2M di token in versioni specifiche.

Cosa significa per te?

- Puoi mettere un intero libro, un codebase, un mese di chat nel prompt.
- **Più contesto ≠ sempre meglio**. Oltre una certa soglia il modello "perde attenzione" su pezzi del prompt (effetto chiamato *lost-in-the-middle*).
- **Più contesto = più costo e più lentezza.** Ogni token in input va elaborato.

Regola pratica: usa il contesto che ti serve, non tutto quello che hai a disposizione.

## 2.4 Sampling: perché lo stesso prompt dà risposte diverse

Quando il modello predice il token successivo, in realtà calcola una **distribuzione di probabilità** su tutti i token possibili. Es:

```
Input: "Il colore del cielo è..."
   "azzurro"  → 38%
   "blu"      → 35%
   "grigio"   → 8%
   "rosa"     → 0.1%
   ...
```

A questo punto bisogna **scegliere** uno dei candidati. I parametri principali del sampling sono:

- **Temperature** (0.0 - 2.0): quanto "creativo" è il modello.
  - `0.0` = sceglie sempre il più probabile (deterministico, ripetitivo).
  - `0.7-1.0` = bilanciato (default tipico).
  - `>1.2` = scelte audaci, a volte sgrammaticate.

- **Top-p** (0-1): considera solo i token che cumulativamente raggiungono p% di probabilità. Es. top-p=0.9 = ignora i token nella "coda lunga" delle improbabilità.

- **Top-k**: considera solo i k token più probabili.

- **Seed**: alcuni modelli accettano un seed per rendere il sampling riproducibile (utile in test).

**Implicazione pratica per gli agenti:** quando vuoi un comportamento deciso e strutturato (es. l'agente sceglie un tool da chiamare), abbassa la temperatura (`0.0-0.3`). Quando vuoi creatività (brainstorming, scrittura), alzala (`0.7-1.0`).

## 2.5 La struttura di un'interazione (chat)

Le API moderne usano un formato a **messaggi** con ruoli:

```python
[
  {"role": "system", "content": "Sei un assistente esperto di cucina italiana."},
  {"role": "user", "content": "Come si fa la carbonara?"},
  {"role": "assistant", "content": "Ti servono guanciale, pecorino..."},
  {"role": "user", "content": "Posso usare la pancetta?"},
]
```

Tre ruoli principali:

- **system**: le istruzioni di base, "chi sei e come ti comporti". Persistono per tutta la conversazione. Il system prompt è dove plasmi il comportamento dell'agente.
- **user**: i messaggi dell'utente.
- **assistant**: le risposte del modello (anche storiche, per dargli memoria della conversazione).

Quando aggiungi il **tool use** (Cap. 6), si aggiungono altri ruoli/strutture: `tool_use` (il modello chiama una funzione) e `tool_result` (risultato che torna al modello).

## 2.6 Cosa sa fare bene un LLM

- Riassumere, riformulare, tradurre.
- Estrarre informazioni strutturate da testo non strutturato.
- Scrivere codice (con limiti — vedi sotto).
- Classificare ("è uno spam? è positivo o negativo?").
- Seguire istruzioni complesse e multi-step se ben formulate.
- Ragionare passo-passo (specialmente i modelli con "thinking" / chain-of-thought).

## 2.7 Cosa NON sa fare bene (limiti da conoscere)

- **Calcoli aritmetici complessi.** Non ha una calcolatrice dentro: a volte indovina, a volte no. Per i numeri seri, dagli un tool con Python.
- **Verità factuali rare o recenti.** Il modello ha una *knowledge cutoff* (data dell'ultimo training). Per fatti aggiornati o nicchia, serve RAG (Cap. 7) o web search.
- **Coerenza su contesti lunghissimi.** Anche con 1M di token può perdere dettagli.
- **Conteggi precisi.** "Quante 'r' ci sono in strawberry?" è famoso per metterli in difficoltà — perché vede token, non lettere.
- **Sa dire "non lo so".** Spesso preferisce inventare (fenomeno detto **allucinazione**). Vedi Cap. 13.
- **Ragionamento causale rigoroso.** È bravo a *sembrare* di ragionare, ma su problemi nuovi fuori dal training spesso sbaglia.

## 2.8 Modelli e famiglie (panoramica 2026)

I principali "fornitori" di LLM:

| Famiglia | Aziende | Punti di forza |
|---|---|---|
| **Claude** (Anthropic) | Opus, Sonnet, Haiku | Coding, ragionamento lungo, sicurezza, lunghi contesti |
| **GPT** (OpenAI) | GPT-5, GPT-5 Mini | Ecosistema, tool use maturo, ChatGPT plugin |
| **Gemini** (Google) | Gemini 2 Pro/Flash | Multimodalità (audio/video), context window enormi |
| **Llama** (Meta) | Llama 4, varie taglie | Open weights, self-hosted |
| **Mistral** (Mistral AI) | Mistral Large, Mixtral | Open weights, ottimi modelli europei |
| **Qwen, DeepSeek** | varie | Modelli aperti molto competitivi |

Ogni famiglia ha modelli di dimensioni diverse, con il classico tradeoff:
- **Modelli grandi** (Opus, GPT-5, Gemini Ultra): più capaci, più costosi, più lenti.
- **Modelli piccoli** (Haiku, Mini, Flash): meno capaci ma molto più economici e veloci. Spesso bastano.

Regola pratica per agenti: **prototipa con il modello più capace, in produzione passa al più piccolo che mantiene la qualità accettabile**. Risparmi 5-10x sui costi.

## 2.9 Pratica: senti la differenza

Vai su [chat.openai.com](https://chat.openai.com) o [claude.ai](https://claude.ai) e fai questi tre esperimenti:

1. **Conta le 'a' in "abracadabra".** Se il modello ti risponde male, hai visto il problema dei token.
2. **Chiedi: "Calcola 837 × 924 senza usare strumenti."** Confronta col risultato vero (773.388). Spesso sbagliano.
3. **Chiedi la stessa cosa due volte:** "Inventami un nome per un caffè letterario." Vedrai risposte diverse — è il sampling al lavoro.

Ti darà un'intuizione che nessun grafico potrebbe darti.

## 2.10 Da ricordare

- **L'LLM predice token, uno alla volta.** Tutto il resto deriva da questa cosa semplice.
- **Token = unità di misura.** Costi, contesto, prestazioni: tutto è in token.
- **Temperature regola la creatività.** Bassa per agenti decisionali, alta per scrittura.
- **System prompt > user prompt** per plasmare il comportamento di base.
- **I modelli grandi non sempre servono.** Inizia grande, ottimizza piccolo.
- **Conoscere i limiti** (calcoli, fatti recenti, conteggi) ti salva da brutte sorprese.

## 2.11 Errori tipici

- **Pensare che il modello "sappia" qualcosa.** Sa pattern, non fatti. Per i fatti, dagli fonti (RAG, tool).
- **Usare temperature alta per agenti che devono decidere.** Risultato: l'agente cambia idea, sceglie tool sbagliati, va in loop.
- **Riempire il context window per sicurezza.** Più contesto = più rumore. Metti solo l'essenziale.
- **Affidarsi a un solo modello "perché va bene".** Modelli diversi sono bravi in cose diverse. Testane più di uno per il tuo caso d'uso.

---

Ora che sai com'è fatto il motore, vediamo come si costruisce intorno la **carrozzeria** dell'agente.

→ [Capitolo 3 — Anatomia di un agente](03-anatomia-di-un-agente.md)
