# 15. Casi d'uso e workflow reali

In questo capitolo niente teoria nuova. Solo **dove gli agenti stanno cambiando lavoro reale**, con pattern che puoi adottare. Pensalo come un menù da cui scegliere il prossimo progetto da provare.

## 15.1 Coding e sviluppo software

### Pair programming intensivo
Strumenti: Claude Code, Cursor, Aider, Windsurf.

Cosa cambia: la velocità di scrittura del codice "boilerplate" (CRUD, integrazioni, refactor meccanici) crolla. Il dev si concentra su **architettura, edge case, code review**.

Pattern tipico:
1. Scrivi spec (il "cosa" e il "perché").
2. L'agente propone piano + diff.
3. Tu rivedi, correggi, iteri.
4. Test eseguiti automaticamente.
5. Commit.

Risultato realistico: 2-4x produttività su task standard, marginale su problemi davvero nuovi.

### Code review automatica
Agente che gira su ogni PR e commenta:
- Bug potenziali.
- Pattern inconsistenti col resto del codebase.
- Test mancanti.
- Security issue (SQL injection, secret hardcoded).

Esempi: GitHub Copilot Code Review, Anthropic `/ultrareview`, CodeRabbit.

### Debug e incident response
Agente che, dato un log o uno stack trace:
- Identifica la causa probabile.
- Cerca il codice rilevante.
- Propone una fix.

In on-call, riduce il "time to first hypothesis" da 30 minuti a 1.

### Migrazione e refactor
Esempi reali: migrazione Python 2 → 3, AngularJS → React, monolite → microservizi.

Approccio:
1. L'agente analizza il codebase, mappa i pattern.
2. Propone strategia di migrazione.
3. Esegue passi piccoli, con test a ogni passo.
4. L'umano rivede, approva.

Per progetti grossi, agenti come Devin, Coursive, o framework dedicati possono lavorare in autonomia per giorni.

## 15.2 Customer support

### Tier-1 automatico
Agente che gestisce ~70% delle domande standard:
- FAQ.
- Status ordine.
- Reset password.
- Cambio dati.

Quando non sa, **escala** a un umano con il contesto già preparato.

Pattern:
- RAG sulla knowledge base aziendale.
- Tool per CRM, sistema ordini, billing.
- Conversation memory per continuità.
- Confidence threshold: sotto X, escala.

### Smistamento e classificazione
Agente che legge i ticket in arrivo e:
- Classifica (billing, tech support, sales).
- Assegna priorità.
- Routing al team giusto.
- Suggerisce la prima risposta al human agent.

Riduce il tempo di triage del 80-90%.

### Sintesi conversazioni
Dopo una conversazione lunga, l'agente produce:
- Riassunto.
- Action items.
- Sentiment del cliente.
- Suggerimenti per il follow-up.

## 15.3 Ricerca e analisi

### Deep research
Strumenti come ChatGPT Deep Research, Perplexity Pro, Gemini con Workspace.

Pattern:
1. Domanda complessa ("analizza il mercato X negli ultimi 5 anni").
2. Agente naviga il web, legge decine di fonti, fa cross-check.
3. Produce report strutturato con citazioni.

Il lavoro che richiedeva 1-2 giornate di un junior analyst si fa in 30 minuti, con qualità sufficiente per la prima draft.

### Analisi di dati
ChatGPT Code Interpreter, Claude con tool `code_execution`, Hex Magic, Julius AI.

Pattern:
1. Carichi un CSV/Excel.
2. Spieghi cosa vuoi capire.
3. L'agente scrive Python, esegue, produce grafici.
4. Continui la conversazione: "ora segmenta per regione", "fai test statistico", "esporta Excel".

Per analisi esplorativa è una rivoluzione.

### Document review
Per legali, finance, due diligence:
- Carichi un set di contratti / documenti.
- L'agente estrae clausole specifiche, segnala anomalie, confronta con template.
- Produce checklist da revisionare.

Strumenti: Harvey, Hebbia, Legora (legal); Hebbia, Anvilogic (finance/security).

## 15.4 Scrittura e contenuti

### Long-form writing
Pattern che funziona:
1. Brief chiaro: argomento, audience, tono, lunghezza.
2. Outline prima del testo.
3. Iterazioni sull'outline.
4. Espansione sezione per sezione.
5. Editing finale (umano o assistito).

Per blog post, articoli, guide: una mezza giornata di lavoro umano si riduce a un'ora di review.

### Newsletter e brief periodici
Agente che ogni mattina:
- Legge le fonti che segui.
- Sintetizza in 5 bullet.
- Manda via email.

Setup di base: 100 righe + cron + LLM.

### Localizzazione
Traduzione + adattamento culturale di contenuti web, manuali, e-commerce. Agenti specializzati con glossari aziendali raggiungono qualità da editing finale, non più da rifusione.

## 15.5 Operations e automazione

### Email management
Agente always-on (Cap. 4) che:
- Classifica le email in arrivo.
- Risponde alle ripetitive (automatica o con bozza).
- Estrae action items in un task manager.
- Segnala le urgenti.

Strumenti: Superhuman AI, Shortwave, agenti custom su Gmail API.

### Calendar e scheduling
Agente che, dato un obiettivo ("riunione con Marco e Giulia entro venerdì"), cerca slot, manda inviti, gestisce conflitti, riprogramma.

Strumenti consumer: Reclaim, Motion. Per aziende: agenti custom su Outlook/Google Calendar.

### Process automation
Workflow business-as-usual con agenti che orchestrano step heterogenei:
- Onboarding cliente: leggere docs, validarli, creare account, inviare benvenuto.
- Procurement: richiesta → preventivi → confronto → ordine.
- Reporting: raccogliere dati da N fonti, formattare, inviare.

Pattern: orchestratore + tool specifici per ogni sistema.

## 15.6 Vendite e marketing

### Lead enrichment
Agente che, dato un lead grezzo (email, azienda):
- Cerca info pubbliche.
- Profila l'azienda (settore, dimensione, segnali di buy).
- Suggerisce angle di outreach.

Strumenti: Clay, Apollo, Crystal.

### Outreach personalizzato
Generazione di messaggi 1:1 sulla base di:
- Profilo del prospect.
- Tuo prodotto.
- Caso d'uso applicabile.

Attenzione: senza tocco umano, scade in spam. Best practice: AI fa la draft, umano rifinisce.

### Content velocity
Da uno spunto, l'agente produce: post LinkedIn, thread X, blog post, newsletter. Ogni canale con tono adattato.

## 15.7 Educazione e formazione

### Tutor personalizzati
Khanmigo (Khan Academy), Duolingo Max, GPT-tutors aziendali.

Pattern:
- Studente chiede.
- L'agente non dà la risposta, fa domande socratiche.
- Adatta difficoltà al livello.
- Tiene memoria del progresso.

### Onboarding aziendale
Nuovi assunti chattano con un agente che ha accesso a tutta la documentazione interna. Domande tipiche ("come si fa X?") risposte 24/7 senza disturbare i colleghi.

### Training simulato
Agenti che impersonano clienti difficili, candidati in colloquio, situazioni di crisis. I trainee si esercitano in sicurezza.

## 15.8 Healthcare (con cautela)

Casi che funzionano oggi:
- **Documentazione clinica**: ascolto consulto, generazione note SOAP, codifica ICD. Strumenti: Abridge, Suki, Nuance DAX.
- **Triage primario**: chatbot che indirizza a specialista o pronto soccorso. Sotto supervisione clinica.
- **Ricerca paper**: sintesi della letteratura medica per il clinico.

Casi che NON funzionano oggi:
- **Diagnosi autonoma**: rischi enormi, regulatory complessa.
- **Decisioni terapeutiche**: l'AI assiste, il medico decide.

Norme: in EU l'AI Act classifica molte applicazioni mediche come "high risk" → richiede certificazioni specifiche.

## 15.9 Legal e compliance (con cautela)

Casi che funzionano:
- **Contract review**: estrazione clausole, confronto con template, flag anomalie.
- **E-discovery**: analisi grandi volumi di documenti per litigation.
- **Legal research**: ricerca giurisprudenza, riassunti di sentenze.
- **Drafting di clausole standard**: l'avvocato rifinisce.

Caveat: l'AI può inventare giurisprudenza. Verifica obbligatoria. Casi famosi di avvocati sanzionati per aver presentato sentenze inesistenti generate da ChatGPT.

## 15.10 Casi un po' più "agentici"

Esempi di prodotti che spingono il livello di autonomia:

- **Devin** (Cognition): agente coder che lavora in autonomia per ore, completa task complessi.
- **OpenAI Operator** / **Anthropic Computer Use**: agenti che usano browser/desktop come un umano (vedono lo schermo, cliccano, digitano).
- **Replit Agent**: build app full-stack da prompt.
- **AutoGPT, BabyAGI** (early): primi tentativi di agenti generalisti, con risultati più dimostrativi che produttivi.
- **Aria** (Opera), **Arc Search**: browser nativi-AI.

Sono spesso ancora **demo impressive** che in produzione tradiscono fragilità. La direzione è chiara, la velocità di maturazione no.

## 15.11 Pattern trasversali

Indipendentemente dal dominio, i workflow vincenti condividono:

1. **Human-in-the-loop su decisioni costose.** L'AI fa la maggior parte, l'umano valida il critico.
2. **Brief strutturati** invece di prompt liberi.
3. **Tool concreti** per parlare con i sistemi reali (CRM, DB, API).
4. **RAG** per far sì che l'agente parli con autorevolezza sui dati specifici.
5. **Memoria di contesto** per non ripetere il setup ogni volta.
6. **Misurazione** di output e outcome.
7. **Disclosure** che è AI-generated quando rilevante.

## 15.12 Quando NON aggiungere agenti

Vale la pena ricordarlo:

- Se il workflow è semplice e codificato, automation tradizionale è meglio.
- Se l'errore è inaccettabile e non c'è verifica umana, attento.
- Se i dati sono troppo sensibili e non hai infra dedicata, aspetta.
- Se i costi non si giustificano, non scalare.

L'AI è un moltiplicatore, non un sostituto del giudizio.

## 15.13 Da scegliere come prossimo progetto

Se sei agli inizi e vuoi un progetto da fare per imparare, ecco una lista in ordine di facilità:

1. **Bot Q&A su un PDF tuo** (RAG + chat). 1-2 ore. Cap. 7, 10.
2. **Riassunto automatico delle tue email del giorno**. 2-3 ore. Tool email + LLM.
3. **Agente di analisi CSV**. 3-4 ore. Code interpreter pattern.
4. **Customer support su FAQ aziendali**. 1-2 giorni. RAG + sviluppo deploy.
5. **Coding agent specializzato per il tuo stack**. 1-2 settimane. Claude Agent SDK + tool su misura.

Iniziare a fare > leggere altre 100 pagine.

## 15.14 Da ricordare

- **Coding, support, ricerca, scrittura, ops, vendite, education**: gli agenti stanno cambiando tutto.
- **Pattern trasversali**: brief strutturato, tool, RAG, human-in-the-loop, misurazione.
- **High-stakes domains (sanità, legge, finanza)**: assistenza sì, autonomia no.
- **Demo impressive ≠ produzione robusta.** Verifica sempre.
- **Inizia da un progetto piccolo e tuo.** Vivere un agente end-to-end è più formativo di 10 corsi.

## 15.15 Errori tipici

- **"L'AI risolverà X."** Senza pattern e workflow concreti, non lo fa.
- **Costruire l'agente più ambizioso al primo tentativo.** Frustrazione assicurata.
- **Trascurare l'integrazione**. La qualità dell'agente dipende dalla qualità dei tool e dati che gli dai.
- **Lanciare senza misurare l'impatto reale.** "L'utente è felice" senza dati.
- **Non capitalizzare sui workflow già esistenti.** L'AI brilla quando si infila nei processi che già fai, non quando devi reinventarli.

---

Ultimo capitolo: il glossario per ricordare i termini, e una lista di risorse per andare oltre la guida.

→ [Capitolo 16 — Glossario e risorse](16-glossario-e-risorse.md)
