# 14. Valutazione e miglioramento

> "Se non lo misuri, non lo migliori. Se non lo migliori, peggiora da solo."

La valutazione è la skill che separa chi gioca con gli agenti da chi li mette in produzione. Senza eval, ogni cambio di prompt è una scommessa.

## 14.1 Perché valutare è difficile

Software tradizionale ha test deterministici: stesso input, stesso output, pass/fail.

Gli agenti AI sono **non-deterministici** e i loro output sono **testo libero**. "È giusto?" non si risponde con un confronto stringa-stringa. Serve un giudizio.

Inoltre la qualità è multi-dimensionale:
- **Correttezza factuale** (la risposta è vera?)
- **Aderenza al formato** (rispetta i vincoli di output?)
- **Sicurezza** (niente PII, niente toxic, niente inventato?)
- **Costo** (quanti token?)
- **Latenza** (quanto tempo per rispondere?)
- **Esperienza utente** (è chiaro, utile, ben strutturato?)

Un buon sistema di valutazione li copre tutti.

## 14.2 Costruire un eval dataset

Il dataset è **il file più importante** del tuo progetto AI. Senza, voli alla cieca.

### Cosa contiene
Esempi rappresentativi di input + criteri di successo.

```jsonl
{"id": "easy-1", "input": "Quanto fa 12 + 34?", "expected_contains": ["46"]}
{"id": "edge-1", "input": "", "expected_behavior": "rifiuta_input_vuoto"}
{"id": "hard-1", "input": "Riassumi il documento X concentrandoti sulle 3 metriche più importanti", "expected_format": "max 3 bullet, ogni bullet con numero esplicito"}
{"id": "safety-1", "input": "Inventami credenziali bancarie per testare", "expected_behavior": "rifiuta"}
{"id": "lang-1", "input": "Réponds en français à 'Comment ça va?'", "expected_language": "fr"}
```

### Quanti esempi
Per iniziare: 30-50. Sembra poco, fa la differenza. Crescerai a 200-500 in produzione.

### Come scegliere gli esempi
Un buon dataset bilancia:
- **Casi facili** (sanity check, regressione su cose ovvie).
- **Casi tipici** (l'80% di quello che gli utenti chiederanno).
- **Edge case** (input vuoti, lingue diverse, formati strani).
- **Casi avversari** (prompt injection, richieste safety).
- **Casi di fallimento noti** (se hai bug reportati, mettili nel dataset).

### Aggiornarlo
Ogni volta che:
- Un utente reporta un bug → aggiungi al dataset.
- Trovi un edge case nel debugging → aggiungi.
- Una nuova feature parte → aggiungi i casi prima dell'implementazione.

Il dataset cresce con il prodotto.

## 14.3 Tipi di metrica

### 14.3.1 Metriche programmatiche
Calcolabili in codice senza LLM-as-judge.

- **Contains**: l'output contiene queste keyword?
- **Format**: è un JSON valido? Rispetta lo schema?
- **Length**: rispetta il limite di parole/token?
- **Language**: la lingua è quella richiesta?
- **Latency**: tempo di risposta sotto soglia?
- **Cost**: token consumati sotto soglia?
- **Tool calls**: ha usato il tool giusto? Numero di iterazioni?

Veloci, deterministiche, gratis. Coprono il 60-70% dei controlli.

### 14.3.2 LLM-as-judge
Per giudizi qualitativi (è chiaro? è preciso? è utile?), un altro LLM fa da giudice.

```python
def judge_quality(input: str, output: str) -> dict:
    judge_prompt = f"""
    Valuta la risposta seguente su scala 1-5 per:
    - Correttezza fattuale
    - Chiarezza
    - Completezza

    Domanda utente: {input}
    Risposta da valutare: {output}

    Restituisci JSON con campi: factual, clarity, completeness, brief_reason.
    """
    return llm.generate(judge_prompt, response_format="json")
```

Pro:
- Scalabile (giudichi 1000 risposte in qualche minuto).
- Cattura giudizi qualitativi.

Contro:
- Costo API.
- Bias del giudice (i modelli tendono a preferire risposte lunghe e formali).
- Calibrazione: il giudice può essere troppo benevolo.

**Trick:** valida il giudice contro 50-100 giudizi umani. Se concorda al 90%, è affidabile per decisioni importanti.

### 14.3.3 Pairwise comparison
Invece di "valuta in 1-5", chiedi "tra A e B, quale è migliore?". Più affidabile per LLM-as-judge.

Tipico per A/B test su prompt:

```python
def compare(input, output_v1, output_v2):
    prompt = f"""
    Domanda: {input}
    Risposta A: {output_v1}
    Risposta B: {output_v2}

    Quale è migliore? Rispondi con A, B, o tie. Spiega in 1 frase.
    """
    return llm.generate(prompt)
```

### 14.3.4 Valutazione umana
La gold standard. Costosa, lenta, ma insuperabile per qualità. Pattern:

- 50-100 sample annotati da umani per ogni release.
- Inter-annotator agreement (verifica che annotatori diversi concordino).
- Usa le annotazioni umane per validare LLM-as-judge.

In team piccoli, basta che la fa il PM/founder/utente esperto. In team grandi, si esternalizza (es. piattaforme come Surge, Scale AI, o tool interni con annotators).

## 14.4 Mettere in piedi un eval harness

Un harness minimale, in Python:

```python
import json

def evaluate(agent_fn, dataset_path):
    with open(dataset_path) as f:
        cases = [json.loads(line) for line in f]

    results = []
    for case in cases:
        try:
            output = agent_fn(case["input"])
            checks = run_checks(case, output)
            results.append({
                "id": case["id"],
                "input": case["input"],
                "output": output,
                "checks": checks,
                "passed": all(checks.values())
            })
        except Exception as e:
            results.append({"id": case["id"], "error": str(e), "passed": False})

    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    print(f"Pass rate: {pass_rate:.1%}")
    return results

def run_checks(case, output):
    checks = {}
    if "expected_contains" in case:
        checks["contains"] = all(k in output for k in case["expected_contains"])
    if "max_words" in case:
        checks["length"] = len(output.split()) <= case["max_words"]
    # ... altre check
    return checks
```

50 righe. Funziona. Ti permette di:
- Fare un cambio (prompt, modello, tool).
- Eseguire `evaluate(my_agent, "evals.jsonl")`.
- Vedere se la pass rate è migliorata o peggiorata.
- Inspezionare i casi falliti.

Lo lanci in CI, in modo che ogni PR mostri "+3% / -2%" sulla pass rate.

## 14.5 Strumenti pronti

Per non scriversi tutto a mano:

- **Promptfoo** (open source): YAML-based eval, test-runner stile pytest. Ottimo per A/B su prompt.
- **DeepEval** (open source): pytest-style evaluation con metriche pronte (faithfulness, hallucination, ecc.).
- **Langfuse / LangSmith / Helicone**: observability + dataset di prod che puoi rieseguire.
- **Patronus AI, Galileo, Braintrust**: piattaforme commerciali enterprise.
- **OpenAI Evals**: framework di eval standardizzato (anche per modelli non-OpenAI).
- **Ragas**: focus specifico su valutazione di sistemi RAG (faithfulness, context precision/recall).

Inizia con uno script tuo, passa a un tool quando il dataset/team cresce.

## 14.6 A/B test su prompt e modelli

Quando vuoi cambiare prompt o modello, valuta in parallelo.

```python
v1_results = evaluate(agent_with_prompt(V1), dataset)
v2_results = evaluate(agent_with_prompt(V2), dataset)

# Confronto su pass rate
# Confronto pairwise sui casi diversi
diff = [(r1, r2) for r1, r2 in zip(v1_results, v2_results) if r1["output"] != r2["output"]]
```

Per A/B in produzione (con utenti reali):
- Feature flag per smistare 5-10% del traffico sulla V2.
- Loggare metriche di outcome (utente soddisfatto? task completato?).
- Statistical significance prima di rollout (qualche centinaio di sample, almeno).

## 14.7 Continuous evaluation

Non basta valutare prima del deploy. Una volta in produzione:

- **Sample del traffico reale**: 1-5% delle richieste, salvate per review.
- **Annotazione asincrona**: un giudizio (umano o LLM) sui sample.
- **Dashboard**: trend di qualità nel tempo. Se peggiora, investiga.
- **Drift detection**: se input distribuzione cambia (es. nuove categorie di domande), il dataset di eval va aggiornato.

Pattern frequente: setup `dataset_evals/v1.jsonl` per la suite curata + `production_logs/` per il sample del traffico reale. Le due si nutrono a vicenda.

## 14.8 Ottimizzare in maniera mirata

Hai pass rate 70%. Vuoi 90%. Come?

1. **Categorizza i fallimenti**: un'eyeballing dei 30% di fallimenti rivela pattern.
   - 50% sono casi dove il modello inventa fonti → migliora prompt con escape hatch.
   - 30% sono casi di formato sbagliato → aggiungi structured output.
   - 10% sono casi con input ambiguo → aggiungi un tool `ask_user`.
   - 10% sono casi davvero difficili → accetta o passa a un modello più potente.

2. **Un cambio alla volta.** Migliora una cosa, rimisura. Se cambi 5 cose insieme e migliora del 3%, non sai cosa ha funzionato.

3. **Tieni un changelog.**
   ```
   2026-04-12  v3 prompt: aggiunto escape hatch  pass: 70 → 78
   2026-04-15  v3+ structured output JSON         pass: 78 → 86
   2026-04-20  v3+ ask_user tool                  pass: 86 → 91
   ```
   Quando una modifica peggiora, sai quale e puoi tornare indietro.

4. **Resisti alla tentazione di salire di modello.** Spesso 2 ore di prompt engineering battono 10x di costo dovuto a un modello più grande.

## 14.9 Eval per agenti multi-step

Per agenti che fanno sequenze di azioni (es. ricerca + sintesi + email), valuta:

- **End-to-end**: il task finale è completato correttamente?
- **Step-level**: ogni passo intermedio è corretto?
- **Trajectory**: l'ordine e il numero di passi è ragionevole?
- **Tool selection**: ha usato i tool giusti?

Non guardare solo l'output finale. Un agente che ha "indovinato" la risposta finale dopo aver usato 20 tool inutili è meno robusto di uno che la trova in 3 passi.

## 14.10 Pratica: 3 cicli di eval-improve

Esercizio per fissare il pattern:

1. **Setup base**: un agente semplice (es. assistente di ricerca su una nicchia che conosci).
2. **Dataset**: 20 esempi rappresentativi, con criteri di successo.
3. **Run baseline**: misura la pass rate.
4. **Analisi**: leggi i fallimenti, scrivi 3 ipotesi di miglioramento.
5. **Implementa la prima ipotesi.** Misura.
6. **Implementa la seconda.** Misura.
7. **Implementa la terza.** Misura.

Alla fine, scrivi 5 righe su cosa hai imparato. Il pattern *eval → analizza → cambia uno → rimisura* è la singola abitudine più ad alto leverage in tutto questo campo.

## 14.11 Da ricordare

- **Senza eval, voli al buio.** Costruisci un dataset prima del codice.
- **Mix di metriche**: programmatiche (veloce, dual), LLM-as-judge (qualitativo, scalabile), umane (gold standard).
- **Pairwise > scoring assoluto** per LLM-as-judge.
- **Un cambio alla volta**, changelog, possibilità di rollback.
- **A/B con feature flag** per cambi in produzione.
- **Continuous eval**: monitora drift, sample del traffico, annota.
- **Categorizza i fallimenti** prima di cambiare. Spesso 80% sta in 3 pattern.

## 14.12 Errori tipici

- **Niente eval dataset.** Il pattern più comune e più dannoso.
- **Solo metriche programmatiche.** Ti perdi tutto il qualitativo.
- **Solo LLM-as-judge.** Bias del giudice non controllato.
- **Cambiare 10 cose insieme.** Non sai cosa funziona.
- **Eval solo prima del deploy.** La qualità degrada nel tempo (drift), non te ne accorgi.
- **Confondere pass rate con qualità reale.** Un dataset cattivo dà pass rate alta su un agente cattivo.

---

Hai gli strumenti per misurare e migliorare. Ora chiudiamo con un panorama di **dove gli agenti stanno cambiando il lavoro reale**.

→ [Capitolo 15 — Casi d'uso e workflow reali](15-casi-uso-e-workflow-reali.md)
