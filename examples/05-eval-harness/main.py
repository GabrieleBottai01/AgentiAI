"""
Esempio 05 — Eval harness con dataset .jsonl
Capitolo 14 della guida.

Valuta un agente/prompt su un dataset di test:
- Programmatic checks (contains, format, max_words)
- LLM-as-judge per qualità qualitativa
- Pass rate, breakdown per categoria, casi falliti
- Riproducibile (run salvato come .json)

Esegui:
    python main.py                      # esegue eval con prompt v1
    python main.py --prompt v2          # eval con prompt v2 (per A/B)
    python main.py --judge              # abilita LLM-as-judge (~+€0.05)
"""

import argparse
import json
import os
import time
from pathlib import Path

from anthropic import Anthropic


HERE = Path(__file__).parent
DATASET = HERE / "evals.jsonl"


# ----- I prompt da testare -----
PROMPTS = {
    "v1": "Sei un assistente conciso. Rispondi alla domanda in massimo 100 parole, in italiano.",
    "v2": (
        "Sei un assistente preciso e conciso.\n"
        "Stile:\n"
        "- Italiano, frasi brevi.\n"
        "- Massimo 100 parole.\n"
        "- Per i numeri, usa cifre (es. 5 non cinque).\n"
        "- Se non sai, dillo invece di inventare.\n"
    ),
}


# ----- Generazione output -----
def generate_response(client: Anthropic, prompt_key: str, user_msg: str) -> str:
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=PROMPTS[prompt_key],
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text


# ----- Programmatic checks -----
def run_programmatic_checks(case: dict, output: str) -> dict:
    checks = {}
    if "expected_contains" in case:
        checks["contains"] = all(k.lower() in output.lower() for k in case["expected_contains"])
    if "expected_not_contains" in case:
        checks["not_contains"] = all(k.lower() not in output.lower() for k in case["expected_not_contains"])
    if "max_words" in case:
        checks["max_words"] = len(output.split()) <= case["max_words"]
    if "min_words" in case:
        checks["min_words"] = len(output.split()) >= case["min_words"]
    if "expected_language" in case:
        # Heuristica: presenza di articoli/parole comuni
        if case["expected_language"] == "it":
            checks["language_it"] = any(w in output.lower() for w in [" il ", " la ", " e ", " di ", " che "])
        elif case["expected_language"] == "en":
            checks["language_en"] = any(w in output.lower() for w in [" the ", " and ", " of ", " that "])
    return checks


# ----- LLM-as-judge -----
JUDGE_PROMPT = """Sei un valutatore. Giudica la risposta di un assistente AI rispetto a una domanda.

DOMANDA: {input}

RISPOSTA: {output}

Valuta su 3 dimensioni con scala 1-5:
- factual: la risposta è factualmente corretta?
- clarity: è chiara e ben strutturata?
- conciseness: è concisa, senza fluff?

Rispondi SOLO con JSON: {{"factual": N, "clarity": N, "conciseness": N, "reason": "frase breve"}}
"""


def llm_judge(client: Anthropic, case: dict, output: str) -> dict:
    prompt = JUDGE_PROMPT.format(input=case["input"], output=output)
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text
    # Extract JSON
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception as e:
        return {"factual": 0, "clarity": 0, "conciseness": 0, "reason": f"parse error: {e}"}


# ----- Eval runner -----
def evaluate(client: Anthropic, prompt_key: str, use_judge: bool):
    cases = [json.loads(l) for l in DATASET.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Eval con prompt={prompt_key}, judge={use_judge}, dataset={len(cases)} casi")
    print("-" * 60)

    results = []
    t0 = time.time()
    for i, case in enumerate(cases, 1):
        try:
            output = generate_response(client, prompt_key, case["input"])
            checks = run_programmatic_checks(case, output)
            judge = llm_judge(client, case, output) if use_judge else None
            passed = all(checks.values()) if checks else True
            results.append({
                "id": case["id"],
                "input": case["input"],
                "output": output,
                "checks": checks,
                "judge": judge,
                "passed": passed,
            })
            status = "✓" if passed else "✗"
            judge_score = (
                f" | judge: f={judge['factual']}/c={judge['clarity']}/cz={judge['conciseness']}"
                if judge else ""
            )
            print(f"{i:2d}/{len(cases)} [{status}] {case['id']:15s}  checks: {checks}{judge_score}")
        except Exception as e:
            results.append({"id": case["id"], "error": str(e), "passed": False})
            print(f"{i:2d}/{len(cases)} [ERR] {case['id']:15s}  {e}")

    pass_rate = sum(1 for r in results if r.get("passed")) / max(1, len(results))
    elapsed = time.time() - t0

    print("-" * 60)
    print(f"Pass rate:    {pass_rate:.1%}  ({sum(1 for r in results if r.get('passed'))}/{len(results)})")
    print(f"Latency:      {elapsed:.1f}s, {elapsed/max(1, len(results)):.1f}s/case")

    if use_judge:
        scores = [r["judge"] for r in results if r.get("judge")]
        if scores:
            avg_f = sum(s["factual"] for s in scores) / len(scores)
            avg_c = sum(s["clarity"] for s in scores) / len(scores)
            avg_cz = sum(s["conciseness"] for s in scores) / len(scores)
            print(f"Judge avg:    factual={avg_f:.2f}  clarity={avg_c:.2f}  concise={avg_cz:.2f}")

    # Salva run completo
    out_file = HERE / f"results-{prompt_key}.json"
    out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvato: {out_file.name}")

    # Stampa fallimenti
    failed = [r for r in results if not r.get("passed")]
    if failed:
        print(f"\n{len(failed)} casi falliti:")
        for r in failed[:5]:
            print(f"  - {r['id']}: {r.get('input', '')[:60]}")
            if r.get("output"):
                print(f"    output: {r['output'][:120]}…")
            print(f"    checks: {r.get('checks', {})}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", choices=["v1", "v2"], default="v1")
    parser.add_argument("--judge", action="store_true", help="enable LLM-as-judge")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Errore: imposta ANTHROPIC_API_KEY"); return

    if not DATASET.exists():
        print(f"Dataset mancante: {DATASET}"); return

    client = Anthropic(api_key=api_key)
    evaluate(client, args.prompt, args.judge)


if __name__ == "__main__":
    main()
