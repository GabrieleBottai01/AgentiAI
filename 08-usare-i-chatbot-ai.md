# 8. Usare i chatbot AI: ChatGPT, Claude.ai, Gemini

Prima di costruire agenti, impara a **usarli bene** sui prodotti consumer. È il modo più veloce per sviluppare intuito su cosa funziona e cosa no, e per molti compiti di vita reale è anche tutto ciò che ti serve.

## 8.1 Le tre interfacce principali

| Prodotto | URL | Chi lo fa | Punti di forza |
|---|---|---|---|
| **ChatGPT** | chat.openai.com | OpenAI | Ecosistema più ricco (GPT, Plugin, Code Interpreter, GPTs custom) |
| **Claude** | claude.ai | Anthropic | Ottimo per scrittura/coding, contesti lunghi, "Projects" |
| **Gemini** | gemini.google.com | Google | Integrazione con Google (Gmail, Docs, Drive), multimodalità |

Tutte e tre offrono:
- Tier gratuito limitato.
- Tier a pagamento (~20€/mese) con modelli più capaci e limiti più alti.
- App mobile e desktop.

Le differenze pratiche cambiano spesso. La tua scelta dovrebbe basarsi su:
- **Quale ecosistema usi già** (Google Workspace? → Gemini si integra bene).
- **Per cosa lo usi** (scrittura/coding intenso? → Claude tende a vincere).
- **Cosa ti piace come UX**.

Provarli tutti per due settimane è la cosa più sensata.

## 8.2 Le funzionalità che cambiano la vita

Tutte e tre offrono, con nomi diversi, queste funzionalità:

### Memoria
ChatGPT "Memory", Claude "Project knowledge", Gemini "Saved info". Salvano fatti su di te tra una conversazione e l'altra.

**Cosa metterci:**
- Il tuo ruolo, tono preferito ("rispondi in italiano, stile diretto").
- Convenzioni del tuo team (linguaggio, librerie, framework).
- Vincoli persistenti ("uso macOS, prediligo Python 3.12").

**Cosa NON metterci:**
- Segreti, password, dati sensibili (i provider possono usare le conversazioni per training, salvo opt-out).
- Informazioni che cambiano spesso (le riscriverai ogni volta).

### Allegati e file
Puoi caricare PDF, immagini, fogli Excel, codice. Il modello li legge e ci ragiona sopra.

**Casi d'uso tipici:**
- "Riassumi questo PDF di 80 pagine."
- "Estrai i dati di questa fattura in CSV."
- "C'è qualcosa di strano in questo grafico?" (multimodale: immagine + ragionamento).

**Limite:** PDF molto grandi possono saturare il context o essere processati a pezzi. Per bibbie di documenti, RAG (Cap. 7).

### Code execution / Code Interpreter
Il modello scrive ed **esegue codice Python** in un sandbox per:
- Analizzare un CSV.
- Generare grafici.
- Convertire formati di file.
- Fare calcoli precisi.

Questo è il "code-generating agent" di cui parlavamo nel Cap. 4. Velocissimo per task data-driven.

### Web search
Il modello cerca nel web durante la risposta. Essenziale per fatti aggiornati (oltre la knowledge cutoff).

ChatGPT, Claude e Gemini hanno tutti questa funzione. Si attiva di default quando il modello "sente" che serve, o tramite un toggle esplicito.

### Image generation
Genera immagini da prompt. Dall'identità grafica per uno slide deck a un mockup di UI. Le qualità variano: DALL-E 3 in ChatGPT, Imagen in Gemini, Sora per video.

### Voice / mode conversazionale
App mobile: parli, il modello ti risponde con voce. Sorprendentemente buona, ottima per prompt lunghi mentre cammini.

### Custom GPTs / Projects / Gems
Versioni "configurate" dell'AI con prompt e knowledge dedicati. Esempi:
- ChatGPT Custom GPT con istruzioni specializzate (es. "il mio coach di scrittura", "esperto di legge italiana").
- Claude Project con un set di documenti caricati (es. tutti i contratti del 2025).
- Gemini Gem con un ruolo personalizzato.

Sono il modo più semplice per "costruire un agente" senza scrivere codice.

## 8.3 Workflow consigliati

### Workflow 1 — Brainstorming
1. Apri una nuova chat.
2. Spiega il problema in 3-4 frasi, dai contesto sul tuo target.
3. Chiedi 10 idee, ognuna con "perché potrebbe funzionare" e "rischi".
4. Scegli la rosa di 3 e chiedi di approfondirle.
5. Per la favorita, chiedi un piano di esecuzione.

### Workflow 2 — Scrittura (articolo, email, post)
1. Spiega: argomento, audience, tono, lunghezza, formato.
2. Chiedi un **outline** prima del testo completo.
3. Itera sull'outline finché non ti convince.
4. Solo allora chiedi il testo completo.
5. Editing: chiedi "rendilo più diretto", "togli aggettivi", "aggiungi un esempio nel paragrafo 3".

Saltare l'outline è l'errore più comune. Il modello scriverà 1000 parole su un'angolazione che non ti piace, e farai più fatica a riscrivere che a partire da capo.

### Workflow 3 — Analisi documento
1. Carica il documento.
2. Inizia con: "Riassumi in 5 bullet" → ti calibri sul contenuto.
3. Domande mirate: "Cosa dice della sezione X?", "Quali sono le scadenze?".
4. Estrazione strutturata: "Estrai le date in formato YYYY-MM-DD, una per riga".

### Workflow 4 — Imparare un nuovo argomento
1. "Spiegami X come se fossi nuovo. Parti dal contesto, poi i concetti chiave, poi un esempio."
2. "Adesso testami: fammi 5 domande in ordine crescente di difficoltà."
3. Risponde tu, lui corregge.
4. "Quali sono i misconcetti tipici di chi inizia con X?"
5. "Risorsa migliore per approfondire?" (verifica i link suggeriti — può inventare).

### Workflow 5 — Coding (light)
1. Descrivi il problema con un esempio di input/output desiderato.
2. Specifica linguaggio, libreria, vincoli (no dipendenze esterne, ecc.).
3. Chiedi codice + spiegazione.
4. Test: copia in un editor, esegui. Se non funziona, mostra l'errore al modello.
5. Per progetti seri, passa a Claude Code (Cap. 9), non a chat.

## 8.4 Tips che fanno la differenza

- **Inizia ogni chat con il contesto.** "Sono un avvocato civilista, l'utente di questo documento è un cliente non tecnico." Cambia tutta la qualità.
- **Una chat = un argomento.** Apri una nuova chat per un task nuovo. Mischiare confonde il modello e la tua memoria.
- **Salva i prompt buoni.** Se trovi un prompt che funziona, mettilo in una nota. Tornerà utile.
- **Usa "Continue" o "Espandi"** se la risposta è incompleta.
- **"Critica la tua risposta"** prima di accettare. Spesso emergono cose che mancavano.
- **Confronta modelli** sullo stesso prompt quando hai dubbi. ChatGPT e Claude possono dare prospettive diverse utili.
- **Per task ripetitivi**, crea un Custom GPT / Project / Gem. Riutilizzi prompt e contesto senza ripetere ogni volta.

## 8.5 Cosa NON fare

- **Non incollare dati sensibili.** Codice fiscale, credenziali, IP confidenziale aziendale: usa modalità con opt-out training, oppure prodotti enterprise (ChatGPT Enterprise, Claude Team) con policy di non training.
- **Non fidarti dei link.** I modelli inventano URL plausibili che non esistono. Verifica sempre.
- **Non delegare decisioni critiche** senza verifica. Diagnosi mediche, consulenza legale, finanziaria: l'AI è uno strumento di supporto, non un decisore.
- **Non aspettarti coerenza tra turni**. Se chiedi due volte la stessa cosa con piccole variazioni, può rispondere diverso. È normale.
- **Non lottare contro il modello.** Se non capisce dopo 3 tentativi, riformula o passa a un altro modello.

## 8.6 Privacy e training: cosa devi sapere

Per default, i provider possono usare le tue conversazioni per migliorare i modelli. Per evitarlo:

- **ChatGPT**: Settings → Data Controls → "Improve the model for everyone" → OFF.
- **Claude**: Le conversazioni in Pro non vengono usate per training di default. Verifica nelle settings.
- **Gemini**: Activity → Web & App Activity → controlla cosa viene salvato.

Per ambito professionale, prediligi versioni Enterprise/Team con SLA di non training scritte nel contratto.

## 8.7 Esercizio: il "test della giornata"

Per una settimana, ogni volta che stai per fare qualcosa che richiede pensiero o scrittura, chiediti: **"posso farlo prima con un AI?"**. Non delegare cieco, ma usalo come **acceleratore**.

Lista di task tipici dove cambia tutto:

- Scrivere una email difficile (richiamo a un fornitore, condoglianze, richiesta scomoda).
- Prendere appunti da una riunione (audio → testo → riassunto + action items).
- Analizzare un Excel di 50 righe (chiedi di trovare i pattern).
- Tradurre un testo tecnico (cura il glossario).
- Spiegare un concetto a tuo figlio in modo semplice.
- Generare 10 nomi per un progetto.
- Riassumere un articolo lungo.
- Validare un'idea ("trova i 5 buchi più grandi in questa proposta").

Dopo una settimana avrai un'intuizione naturale di "quando l'AI mi conviene".

## 8.8 Da ricordare

- **ChatGPT, Claude, Gemini** sono il punto di partenza. Provali, scegli quello che si adatta meglio al tuo lavoro.
- **Memoria, allegati, code interpreter, web search**: le funzionalità trasversali che usi quotidianamente.
- **Workflow > prompt singolo**. Outline prima del testo, brainstorming prima della soluzione, riassunto prima delle domande di dettaglio.
- **Custom GPT / Project / Gem** per task ripetitivi: configuri una volta, riusi sempre.
- **Privacy**: opt-out training, mai dati sensibili, prediligi Enterprise per uso professionale.

## 8.9 Errori tipici

- **Aspettarsi risultati senza dare contesto.** "Scrivimi un'email" → mediocre. "Scrivimi un'email a un cliente B2B che si lamenta del ritardo, tono cordiale ma fermo, in italiano" → eccellente.
- **Restare con prompt singolo.** Le 5 risposte successive ti raffinano il risultato.
- **Cercare l'unica frase magica.** Non esiste; esiste un workflow buono.
- **Usare ChatGPT per coding serio.** Ottimo per snippet; per progetti, Claude Code o Cursor sono più produttivi.
- **Non sfruttare la voice mode** per pensare a voce alta. Cammini, parli, ricevi risposte. Cambia il modo di lavorare.

---

I chatbot sono il livello "consumer". Per chi sviluppa, esiste qualcosa di molto più potente: un agente AI dentro il tuo terminale.

→ [Capitolo 9 — Claude Code per sviluppatori](09-claude-code-per-sviluppatori.md)
