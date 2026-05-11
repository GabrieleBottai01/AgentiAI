"""
Esempio 01 — Loop minimale di un agente
Capitolo 3 della guida.

Questo è il "70 righe" che dimostra come un agente reale è strutturato:
- modello che decide
- tool che agiscono
- loop che mette tutto insieme
- stop criterion (max iterations + natural stop)

Esegui: python main.py
"""

import json
import os
from datetime import datetime, timezone

from anthropic import Anthropic


# ----- Tool definitions -----
TOOLS = [
    {
        "name": "calculator",
        "description": (
            "Esegue un'espressione aritmetica Python (es. '2+2', '15*23/4'). "
            "Usa SOLO per calcoli numerici."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Espressione aritmetica valida in Python"},
            },
            "required": ["expression"],
        },
    },
    {
        "name": "current_time",
        "description": "Restituisce data e ora correnti UTC in formato ISO-8601.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def tool_calculator(expression: str) -> str:
    """ATTENZIONE: eval è insicuro. In produzione usare un parser dedicato."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"errore: {e}"


def tool_current_time() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


TOOL_FUNCS = {
    "calculator": tool_calculator,
    "current_time": tool_current_time,
}


# ----- Agent loop -----
def run_agent(client: Anthropic, goal: str, max_iterations: int = 10) -> str:
    messages = [{"role": "user", "content": goal}]

    for step in range(1, max_iterations + 1):
        print(f"\n→ Iterazione {step}")
        resp = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            system="Sei un assistente preciso. Usa i tool quando servono. Risposte concise.",
            tools=TOOLS,
            messages=messages,
        )
        # Aggiungi la risposta dell'assistente alla history
        messages.append({"role": "assistant", "content": resp.content})

        # Stop naturale: niente tool da chiamare
        if resp.stop_reason != "tool_use":
            text_blocks = [b for b in resp.content if b.type == "text"]
            return text_blocks[-1].text if text_blocks else "(no response)"

        # Esegui i tool richiesti
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            print(f"  • tool: {block.name}({json.dumps(block.input)})")
            fn = TOOL_FUNCS.get(block.name)
            result = fn(**block.input) if fn else f"errore: tool '{block.name}' sconosciuto"
            print(f"    → {result}")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    return "Limite di iterazioni raggiunto."


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Errore: imposta ANTHROPIC_API_KEY")
        return

    client = Anthropic(api_key=api_key)

    goal = "Quanti minuti sono passati dalla mezzanotte UTC fino ad adesso? Spiega il calcolo."
    print(f"OBIETTIVO: {goal}")

    answer = run_agent(client, goal)
    print(f"\n=== RISPOSTA FINALE ===\n{answer}")


if __name__ == "__main__":
    main()
