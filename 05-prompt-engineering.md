# 5. Prompt engineering: l'arte di chiedere

> "Il prompt engineering è l'80% del lavoro per far funzionare bene un agente. Il restante 20% è scegliere il modello giusto e dargli i tool giusti."

Imparare a scrivere prompt efficaci è la skill più alto-leveraged in questo intero campo. Vale per chi usa ChatGPT, per chi costruisce agenti, per chi configura un sistema di customer support.

## 5.1 Cos'è davvero un "prompt"

Un prompt è **tutto il testo che il modello vede prima di rispondere**. Include:

- Il **system prompt** (le istruzioni di base, "chi sei e come ti comporti").
- L'**user message** (la richiesta corrente).
- La **history** (turni precedenti, se è una conversazione).
- I **tool result** (output dei tool nei turni passati).
- Eventuali **documenti** che hai allegato.

Quando dico "il prompt", spesso intendo tutto questo insieme. Il modello non distingue: per lui è una grande sequenza di token.

## 5.2 La struttura di un buon prompt

Un prompt ben fatto ha quasi sempre questi pezzi, in quest'ordine:

1. **Ruolo** — chi è il modello?
2. **Obiettivo** — cosa deve raggiungere?
3. **Contesto** — informazioni di sfondo
4. **Vincoli** — cosa deve / non deve fare
5. **Formato dell'output** — come voglio la risposta
6. **Esempi** (opzionale ma potente)

Esempio cattivo:

> "Riassumi il testo che ti mando."

Esempio buono:

> Sei un editor di una rivista scientifica. Il tuo compito è riassumere paper accademici per lettori non esperti.
>
> Obiettivo: sintetizzare il paper in input in modo che un laureando in giurisprudenza lo capisca.
>
> Vincoli:
> - Massimo 200 parole.
> - Niente gergo tecnico non spiegato.
> - Termina con una bullet list di "3 implicazioni pratiche".
>
> Formato:
> ## Riassunto
> [testo continuativo]
>
> ## Implicazioni pratiche
> - punto 1
> - punto 2
> - punto 3
>
> Paper: """{paper}"""

La differenza in qualità è enorme.

## 5.3 Tecniche fondamentali

### 5.3.1 Few-shot prompting

Mostra al modello 2-3 esempi di input/output desiderati. Le sue risposte successive seguiranno lo stesso pattern.

```
Classifica il sentiment dei tweet in positivo, negativo o neutro.

Tweet: "Adoro questo nuovo telefono!"
Sentiment: positivo

Tweet: "Spedizione lentissima, mai più."
Sentiment: negativo

Tweet: "Arrivato come da descrizione."
Sentiment: neutro

Tweet: "Il design è ok ma la batteria dura niente."
Sentiment:
```

Il modello completerà con `negativo` (o `neutro` se è prudente). Pattern semplice, efficacia altissima.

### 5.3.2 Chain-of-Thought (CoT)

Chiedi al modello di **ragionare passo passo prima** di rispondere.

```
Domanda: Marco ha 12 mele. Ne dà 3 a sua sorella, ne mangia 2,
poi ne compra il doppio di quelle che ha. Quante ne ha alla fine?

Pensa passo passo prima di rispondere.
```

Senza CoT, i modelli sbagliano spesso problemi numerici. Con CoT, accuratezza migliora drasticamente.

I modelli moderni (Claude con "extended thinking", o5/o7 di OpenAI) fanno CoT internamente *senza* che tu glielo chieda. Ma su modelli più piccoli o per task difficili, dirgli "ragiona passo passo" resta utile.

### 5.3.3 Self-consistency

Chiedi N volte la stessa cosa con temperature alta, prendi la risposta più frequente. Trick statistico, costoso in token, utile su problemi quantitativi.

### 5.3.4 Decomposizione

Per task complessi, dividi in sotto-task espliciti:

```
Per scrivere questa relazione legale, segui questa procedura:

PASSO 1: Identifica le parti coinvolte (nome, ruolo).
PASSO 2: Riassumi i fatti in ordine cronologico.
PASSO 3: Elenca le norme di riferimento.
PASSO 4: Scrivi l'analisi giuridica.
PASSO 5: Concludi con raccomandazione.

Esegui un passo alla volta, marcando chiaramente il numero del passo.
```

I modelli seguono molto bene strutture procedurali esplicite.

### 5.3.5 Role priming

Far interpretare un ruolo concreto migliora la qualità per molti task.

```
Sei un Senior Software Engineer con 15 anni di esperienza in sistemi distribuiti.
Stai facendo code review di un junior. Il tuo stile è diretto ma costruttivo.
```

Funziona perché il modello ha visto, in fase di training, milioni di esempi di "esperto X che dice Y". Specificando il ruolo, attivi quella distribuzione.

### 5.3.6 Output strutturato

Se ti serve dati machine-readable, chiedili in JSON con uno schema esplicito:

```
Estrai dal CV le seguenti info, in JSON:

{
  "nome": "string",
  "anni_esperienza": "number",
  "skill": ["string"],
  "ultimo_ruolo": {
    "azienda": "string",
    "titolo": "string",
    "inizio": "YYYY-MM"
  }
}

Rispondi SOLO con JSON valido, niente testo extra.

CV: """{cv}"""
```

Le API moderne offrono **JSON mode** o **structured outputs** che garantiscono che l'output sia un JSON valido conforme allo schema. Usa quelli quando puoi (Cap. 10).

### 5.3.7 Delimitatori

Quando inserisci dati nel prompt, racchiudili in delimitatori chiari (`"""..."""`, `<doc>...</doc>`). Aiuta il modello a distinguere istruzioni da contenuto, e riduce il rischio di **prompt injection** (Cap. 13).

```
Riassumi il testo qui sotto.

<documento>
{contenuto}
</documento>
```

## 5.4 Anti-pattern comuni

### "Per favore" / "ti prego"
Non danneggiano, ma non aiutano. Non perdere token su cortesie.

### Negazioni vaghe
"Non essere troppo lungo" funziona meno di "massimo 100 parole".

### "Sii creativo" senza vincoli
Il modello non sa cosa significa per te. Dai esempi o vincoli concreti.

### Istruzioni contraddittorie
"Sii preciso ma non noioso. Tecnico ma comprensibile a tutti." Il modello sceglierà a caso.

### Prompt enormi senza struttura
Un muro di testo da 4000 parole è difficile da seguire. Usa heading, bullet, sezioni.

### Cambiare formato senza esempio
"Voglio output in formato XML" senza esempio = lotteria. Mostra com'è fatto.

## 5.5 Prompt per agenti (specifico)

Quando il prompt va a un *agente* (non a un chatbot), aggiungi:

- **Lista dei tool disponibili** e quando usarli.
- **Istruzioni sul "quando fermarsi"**.
- **Cosa fare in caso di errore** o di info mancanti.
- **Formato delle risposte intermedie** (se vuoi pulizia).

Esempio (semplificato):

```
Sei un agente di ricerca. Hai questi tool:

- web_search(query): cerca nel web. Usa per fatti aggiornati.
- fetch_url(url): scarica una pagina. Usa per leggere fonti specifiche.
- ask_user(question): chiedi all'utente in caso di ambiguità.

Procedura:
1. Capisci la domanda. Se ambigua, usa ask_user PRIMA di cercare.
2. Cerca info usando web_search. Massimo 3 ricerche.
3. Se i risultati sono incerti, leggi le pagine con fetch_url.
4. Sintetizza la risposta finale citando le fonti.

Stop quando hai una risposta confidente. Se dopo 5 iterazioni non hai
risposta, ammettilo invece di inventare.
```

Notare: dare un'**escape hatch** ("ammettilo invece di inventare") riduce le allucinazioni. Senza, il modello tende a "fabbricare" pur di non dire "non lo so".

## 5.6 Iterazione: il prompt si scrive tre volte

Nessuno scrive un buon prompt al primo tentativo. Il flusso reale è:

1. **V1** — scrivi il prompt minimale.
2. **Test** — prova con 5-10 input rappresentativi.
3. **Annota** dove fallisce.
4. **V2** — aggiungi vincoli/esempi che indirizzano i fallimenti.
5. Ripeti.

Tieni un file `prompts/v3.txt` versionato. I prompt sono codice — meritano git.

## 5.7 Pratica: l'esercizio del prompt che migliora

Apri ChatGPT o Claude.ai e fai questo:

**Step 1**: chiedi "Riassumi questo articolo" + un articolo. Annota il risultato.

**Step 2**: rifai con un prompt strutturato (ruolo, obiettivo, vincoli, formato). Annota.

**Step 3**: aggiungi un esempio di riassunto fatto bene. Rifai. Annota.

Vedrai migliorare la qualità a ogni step. Questo è il loop che farai per ogni agente che costruirai.

## 5.8 Da ricordare

- **Struttura > eloquenza**. Sezioni chiare battono prosa elegante.
- **Esempi > spiegazioni**. Mostrare cosa vuoi è più efficace che descriverlo.
- **Output strutturato (JSON)** quando servono dati, non testo.
- **Delimitatori** per separare istruzioni da contenuto utente.
- **Escape hatches** ("se non sai, dillo") riducono allucinazioni.
- **Itera**. Il primo prompt è quasi sempre subottimale.

## 5.9 Errori tipici

- **Cambiare modello sperando di risolvere problemi di prompt.** Spesso il problema è il prompt, non il modello.
- **Lasciar inventare il formato.** Se ti serve JSON, chiedilo in JSON con schema.
- **Buttare tutto nel system prompt.** Quello che cambia per ogni richiesta va nel user message.
- **Non testare con casi limite.** Input vuoti, in lingue diverse, contraddittori, lunghissimi: il prompt deve gestirli.
- **Trascurare la versione del modello.** Un prompt ottimizzato per Claude 3 può non essere ottimo per Claude 4. Riprovalo quando aggiorni.

---

I prompt da soli non bastano: gli agenti hanno bisogno di **mani e occhi**. Vediamo ora come si dichiarano e si chiamano i tool.

→ [Capitolo 6 — Tool use e function calling](06-tool-use-e-function-calling.md)
