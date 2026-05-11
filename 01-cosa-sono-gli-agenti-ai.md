# 1. Cosa sono gli Agenti AI

> "Un agente AI è un programma che usa un LLM per decidere cosa fare, agire, vedere il risultato e ricominciare."

Tutto qui. Il resto del capitolo serve a far capire perché questa frase semplice cambia tutto.

## 1.1 Dal chatbot all'agente: una storia in tre passi

### Passo 1 — Il chatbot (2022)
Tu scrivi una domanda, il modello risponde. Fine.

```
Tu:    "Qual è la capitale della Francia?"
Bot:   "Parigi."
```

Il bot **non agisce**. Non apre browser, non legge file, non scrive sul tuo disco. È una macchina conversazionale: testo dentro, testo fuori.

### Passo 2 — L'assistente con strumenti (2023)
Diamo al modello la possibilità di **chiamare delle funzioni**. Ora se gli chiedi il meteo, può davvero andarlo a cercare.

```
Tu:    "Che tempo fa a Roma?"
Bot:   [chiama la funzione get_weather("Roma")]
       [riceve "18°, sereno"]
       "A Roma ci sono 18 gradi e cielo sereno."
```

Già più utile, ma è ancora reattivo. Tu chiedi una cosa, lui fa una cosa.

### Passo 3 — L'agente (2024 in poi)
Adesso diamogli un obiettivo, non un comando. E lasciamolo lavorare in **loop**: pensa, agisce, osserva il risultato, ripensa, riagisce. Finché non ha finito.

```
Tu:    "Trova i 5 ristoranti giapponesi meglio recensiti
        a Milano, prenota quello disponibile sabato sera per 4 persone."
Agente: [cerca su Google]
        [legge le recensioni]
        [confronta i risultati]
        [chiama l'API di prenotazione]
        [verifica disponibilità sabato]
        [se il primo è pieno, prova il secondo]
        [conferma]
        "Prenotato Sushi B per sabato 20 alle 21:00."
```

Questo è un agente: **un LLM in un loop, con strumenti e un obiettivo**.

## 1.2 La definizione utile

Mettiamoci d'accordo su una definizione operativa. Un **agente AI** è un sistema software con quattro ingredienti:

1. **Un modello** (LLM) che ragiona e decide.
2. **Strumenti** (tool) che il modello può chiamare per agire sul mondo: leggere file, fare richieste HTTP, eseguire codice, interrogare database.
3. **Un loop** che ripete: il modello produce un'azione → il sistema la esegue → il risultato torna al modello → il modello decide la prossima azione.
4. **Un criterio di stop**: l'agente si ferma quando ha raggiunto l'obiettivo, ha esaurito i tentativi, o l'utente lo interrompe.

Senza il loop e gli strumenti, hai un chatbot. Con loro, hai un agente.

## 1.3 Cosa li rende potenti (e perché ora)

Tre fattori si sono combinati negli ultimi anni:

- **I modelli sanno seguire istruzioni complesse.** GPT-3.5 era già bravo a chiacchierare; i modelli moderni (Claude 4, GPT-5, Gemini 2) sanno *pianificare* e *correggere il tiro* a metà strada.
- **Il "tool use" è diventato standard.** Tutte le API principali offrono un meccanismo strutturato per dichiarare strumenti e farli chiamare al modello (lo vedremo nel Cap. 6).
- **I contesti si sono allargati.** Modelli con 200K-1M token di contesto possono "tenere a mente" interi codebase, libri o conversazioni lunghe.

Risultato: per molti compiti che fino a poco tempo fa richiedevano un esperto umano + script custom, oggi basta un agente ben configurato.

## 1.4 Cosa NON è un agente AI

Per non confondersi, qualche distinzione importante.

| Non è un agente | Cos'è invece |
|---|---|
| Un chatbot (anche bravo) | Un'interfaccia conversazionale senza loop autonomo. |
| Un singolo prompt complesso | Una *generazione singola*. Nessuna azione, nessun feedback. |
| Una pipeline scriptata in cui l'AI fa un solo passo | Un workflow tradizionale che usa l'AI come una funzione. |
| RPA classico (Robotic Process Automation) | Automazione basata su regole, non su decisione. |

La linea è sfumata. **La domanda chiave è: il sistema decide da solo cosa fare al passo successivo?** Se sì, è un agente. Se la prossima azione è già scritta nel codice, è automazione.

## 1.5 Quando ha senso usare un agente (e quando no)

Gli agenti AI sono potenti, ma non gratuiti: costano in token, sono più lenti di una chiamata diretta, e introducono incertezza (lo stesso input può portare a comportamenti leggermente diversi).

**Buoni casi d'uso:**
- Compiti **eterogenei** dove i passi non sono noti in anticipo (ricerca, analisi, debug).
- Lavoro che richiede **giudizio** (riassumere, classificare, redigere).
- Interazioni con **molte fonti** (cercare in più sistemi, aggregare).
- **Esplorazione** in ambienti complessi (un codebase, un dataset).

**Cattivi casi d'uso:**
- Calcoli deterministici (1+1 lo fa Python meglio).
- Operazioni ad alta frequenza in cui ogni millisecondo conta.
- Logiche regolatorie/finanziarie dove serve audit trail rigoroso.
- Compiti dove un errore costa molto e non è recuperabile (cancellazioni irreversibili senza supervisione).

Una buona regola: **se puoi scrivere uno script in 30 minuti, non usare un agente.** Se non sai nemmeno da dove cominciare, l'agente è la soluzione giusta.

## 1.6 Pratica: riconoscere un agente in 30 secondi

Apri questi tre prodotti (anche solo le loro pagine demo) e prova a classificarli:

1. **Un assistente per scrivere email** che aspetta che tu gli dica cosa scrivere → **chatbot**.
2. **Un copilot di codice** che, dato un bug report, esplora il codice, propone una fix, scrive i test e apre la PR → **agente**.
3. **Un'integrazione Slack** che traduce automaticamente i messaggi in inglese quando ne arriva uno in italiano → **automazione con AI**, ma non un agente vero (un solo passo, nessun loop).

L'esercizio diventa intuitivo dopo 4-5 esempi. Tornerai su questa distinzione molte volte.

## 1.7 Da ricordare

- **Un agente AI = LLM + tool + loop + obiettivo.** Senza il loop, è un chatbot.
- **Il valore dell'agente sta nell'autonomia decisionale**: decide lui cosa fare al prossimo passo.
- **Più libertà = più potenza, ma anche più rischio.** Un agente che sbaglia in autonomia può fare danni che un chatbot non può fare.
- **Non sono adatti a tutto.** Per compiti deterministici, scrivere codice tradizionale è meglio.
- **La parola "agente" è abusata.** Quando un prodotto si dichiara "agentico", chiediti: c'è un loop? Ci sono tool? Decide da solo?

## 1.8 Errori tipici

- **Confondere "AI" con "agente".** Gmail usa l'AI per gli smart reply, ma quello non è un agente.
- **Pensare che un agente sia "intelligente" come un umano.** Non lo è. È bravo a seguire pattern e usare strumenti, ma non ha buon senso o esperienza vissuta.
- **Dare all'agente un obiettivo troppo vago.** "Migliora il mio business" non funziona. "Analizza il file vendite.csv e trova i 3 prodotti con calo maggiore nel Q1" funziona.
- **Lasciar correre l'agente senza supervisione su azioni irreversibili.** Cancellazioni, pagamenti, email a clienti: serve una conferma umana, almeno all'inizio.

---

Prossimo capitolo: capiremo il **motore** che fa funzionare tutto questo, l'LLM. Senza scendere in matematica, ma capendo *abbastanza* da usarli bene.

→ [Capitolo 2 — Come funzionano gli LLM](02-come-funzionano-gli-llm.md)
