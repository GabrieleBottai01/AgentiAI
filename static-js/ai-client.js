// =============================================================
// Unified AI client — supporta Anthropic (a pagamento) e Gemini (gratis)
//
// Espone:
//   window.AI.providers                      → metadati dei provider
//   window.AI.getActive()                    → { name, info, key }
//   window.AI.setActive(providerName)
//   window.AI.setKey(providerName, key)
//   window.AI.hasValidActive()               → true se attivo + key presenti
//   window.AI.streamAI({model, system, messages, tools?, temperature?, max_tokens?})
//                                            → async iterator di eventi canonici
//
// Eventi yieldati (canonici, indipendenti dal provider):
//   { type: "text_delta", text }
//   { type: "tool_use", id, name, input }
//   { type: "stop", stop_reason, usage, content }   // content = blocchi da rimettere come assistant turn
//   { type: "error", message }
//
// Il formato dei messaggi in input è ANTHROPIC-STYLE (canonico):
//   messages: [{ role: "user"|"assistant", content: "..." | [blocks...] }]
//   blocks possono essere: {type:"text", text}, {type:"tool_use", id, name, input},
//                          {type:"tool_result", tool_use_id, content}
//
// L'adapter Gemini converte da/verso il formato Google internamente.
// =============================================================

const PROVIDERS = {
  gemini: {
    name: "gemini",
    label: "Gemini di Google",
    pricing: "free",
    pricingLabel: "Gratis",
    storageKey: "gemini_api_key",
    keyPrefix: "AIza",
    consoleUrl: "https://aistudio.google.com/app/apikey",
    consoleLabel: "aistudio.google.com",
    description: "Tier gratuito generoso: 15 req/min, 1500 req/giorno su Gemini 2.5 Flash. Nessuna carta richiesta.",
    models: [
      { id: "gemini-2.5-flash", label: "gemini-2.5-flash (veloce, gratis)", default: true },
      { id: "gemini-2.5-pro", label: "gemini-2.5-pro (più capace, gratis)" },
    ],
  },
  anthropic: {
    name: "anthropic",
    label: "Claude di Anthropic",
    pricing: "paid",
    pricingLabel: "A pagamento",
    storageKey: "anthropic_api_key",
    keyPrefix: "sk-ant-",
    consoleUrl: "https://console.anthropic.com/",
    consoleLabel: "console.anthropic.com",
    description: "Ricarica minima ~$5. Costo tipico: <€0.01 per domanda con Haiku. Imposta un budget cap mensile.",
    models: [
      { id: "claude-haiku-4-5", label: "claude-haiku-4-5 (veloce, economico)", default: true },
      { id: "claude-sonnet-4-6", label: "claude-sonnet-4-6 (bilanciato)" },
      { id: "claude-opus-4-7", label: "claude-opus-4-7 (più capace)" },
    ],
  },
};

const ACTIVE_STORAGE = "ai_provider";

function getActive() {
  const name = localStorage.getItem(ACTIVE_STORAGE) || "gemini";
  const info = PROVIDERS[name] || PROVIDERS.gemini;
  const key = localStorage.getItem(info.storageKey) || "";
  return { name: info.name, info, key };
}

function setActive(name) {
  if (!PROVIDERS[name]) return;
  localStorage.setItem(ACTIVE_STORAGE, name);
}

function getKey(name) {
  const info = PROVIDERS[name];
  if (!info) return "";
  return localStorage.getItem(info.storageKey) || "";
}

function setKey(name, key) {
  const info = PROVIDERS[name];
  if (!info) return;
  if (key) localStorage.setItem(info.storageKey, key);
  else localStorage.removeItem(info.storageKey);
}

function hasValidActive() {
  const a = getActive();
  return !!a.key;
}

// =============================================================
// Anthropic streaming
// =============================================================
async function* streamAnthropic(apiKey, options) {
  const body = {
    model: options.model,
    max_tokens: options.max_tokens || 1024,
    messages: options.messages,
    stream: true,
  };
  if (options.system) body.system = options.system;
  if (options.tools) body.tools = options.tools;
  if (typeof options.temperature === "number") body.temperature = options.temperature;

  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01",
      "anthropic-dangerous-direct-browser-access": "true",
      "content-type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const t = await resp.text();
    yield { type: "error", message: parseProviderError("anthropic", resp.status, t) };
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const blocks = {};
  let stopReason = null;
  let usage = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const chunk = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);

      let eventType = null;
      let dataLine = "";
      for (const line of chunk.split("\n")) {
        if (line.startsWith("event:")) eventType = line.slice(6).trim();
        else if (line.startsWith("data:")) dataLine = line.slice(5).trim();
      }
      if (!dataLine) continue;
      let data;
      try { data = JSON.parse(dataLine); } catch { continue; }

      if (eventType === "content_block_start") {
        const i = data.index;
        const cb = data.content_block;
        blocks[i] = { type: cb.type };
        if (cb.type === "tool_use") {
          blocks[i].id = cb.id;
          blocks[i].name = cb.name;
          blocks[i].partialJson = "";
        } else if (cb.type === "text") {
          blocks[i].text = "";
        }
      } else if (eventType === "content_block_delta") {
        const i = data.index;
        const d = data.delta;
        if (!blocks[i]) continue;
        if (d.type === "text_delta") {
          blocks[i].text += d.text;
          yield { type: "text_delta", text: d.text };
        } else if (d.type === "input_json_delta") {
          blocks[i].partialJson += d.partial_json;
        }
      } else if (eventType === "content_block_stop") {
        const b = blocks[data.index];
        if (b && b.type === "tool_use") {
          let input = {};
          try { input = b.partialJson ? JSON.parse(b.partialJson) : {}; } catch {}
          yield { type: "tool_use", id: b.id, name: b.name, input };
        }
      } else if (eventType === "message_delta") {
        if (data.delta && data.delta.stop_reason) stopReason = data.delta.stop_reason;
        if (data.usage) usage = data.usage;
      } else if (eventType === "message_stop") {
        const content = [];
        Object.keys(blocks).map(Number).sort((a, b) => a - b).forEach(i => {
          const b = blocks[i];
          if (b.type === "text") content.push({ type: "text", text: b.text });
          else if (b.type === "tool_use") {
            let input = {};
            try { input = b.partialJson ? JSON.parse(b.partialJson) : {}; } catch {}
            content.push({ type: "tool_use", id: b.id, name: b.name, input });
          }
        });
        yield { type: "stop", stop_reason: stopReason, usage, content };
      } else if (eventType === "error") {
        yield { type: "error", message: data.error?.message || "Errore sconosciuto" };
      }
    }
  }
}

// =============================================================
// Gemini streaming
// =============================================================

// Converte messaggi canonici (Anthropic-style) → contents Gemini
function canonicalToGemini(messages) {
  return messages.map(m => {
    const role = m.role === "assistant" ? "model" : m.role; // user resta user
    let parts = [];

    if (typeof m.content === "string") {
      parts = [{ text: m.content }];
    } else if (Array.isArray(m.content)) {
      for (const block of m.content) {
        if (block.type === "text") {
          parts.push({ text: block.text });
        } else if (block.type === "tool_use") {
          parts.push({ functionCall: { name: block.name, args: block.input || {} } });
        } else if (block.type === "tool_result") {
          // Gemini formato: functionResponse, role "user"
          let responseObj;
          if (typeof block.content === "string") {
            responseObj = { content: block.content };
          } else {
            responseObj = { content: JSON.stringify(block.content) };
          }
          // Recupera il name dal tool_use_id (nei nostri scenari l'id contiene il name come prefix dopo conversione)
          // Soluzione: il chiamante dovrebbe passare anche il name. Lo estraiamo dal messaggio assistant precedente.
          // Per ora useremo il _toolName se presente nel block (lo settiamo dal codice agent.js).
          parts.push({
            functionResponse: {
              name: block._toolName || block.name || "tool",
              response: responseObj,
            },
          });
        }
      }
    }
    return { role, parts };
  });
}

// Converte tools canonici (Anthropic) → Gemini functionDeclarations
function canonicalToolsToGemini(tools) {
  if (!tools || !tools.length) return undefined;
  return [{
    functionDeclarations: tools.map(t => ({
      name: t.name,
      description: t.description,
      parameters: t.input_schema || { type: "object", properties: {} },
    })),
  }];
}

let geminiToolUseCounter = 0;

async function* streamGemini(apiKey, options) {
  const model = options.model || "gemini-2.5-flash";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:streamGenerateContent?alt=sse&key=${encodeURIComponent(apiKey)}`;

  const body = {
    contents: canonicalToGemini(options.messages),
    generationConfig: {
      temperature: typeof options.temperature === "number" ? options.temperature : 0.7,
      maxOutputTokens: options.max_tokens || 1024,
    },
  };
  if (options.system) body.systemInstruction = { parts: [{ text: options.system }] };
  const tools = canonicalToolsToGemini(options.tools);
  if (tools) body.tools = tools;

  const resp = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const t = await resp.text();
    yield { type: "error", message: parseProviderError("gemini", resp.status, t) };
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const accContent = []; // canonical content blocks ricostruiti
  let textBlockText = "";
  let usage = null;
  let finishReason = null;

  function flushTextBlock() {
    if (textBlockText) {
      accContent.push({ type: "text", text: textBlockText });
      textBlockText = "";
    }
  }

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let lineEnd;
    while ((lineEnd = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, lineEnd).trim();
      buffer = buffer.slice(lineEnd + 1);
      if (!line || !line.startsWith("data:")) continue;
      const dataStr = line.slice(5).trim();
      if (!dataStr) continue;

      let chunk;
      try { chunk = JSON.parse(dataStr); } catch { continue; }

      // Errore embedded?
      if (chunk.error) {
        yield { type: "error", message: chunk.error.message || "Errore Gemini" };
        return;
      }

      const cand = chunk.candidates?.[0];
      if (cand?.content?.parts) {
        for (const part of cand.content.parts) {
          if (typeof part.text === "string" && part.text) {
            textBlockText += part.text;
            yield { type: "text_delta", text: part.text };
          } else if (part.functionCall) {
            flushTextBlock();
            const id = `gemini-tool-${++geminiToolUseCounter}`;
            const tu = {
              type: "tool_use",
              id,
              name: part.functionCall.name,
              input: part.functionCall.args || {},
            };
            accContent.push({ ...tu });
            yield tu;
          }
        }
      }
      if (cand?.finishReason) finishReason = cand.finishReason;
      if (chunk.usageMetadata) {
        usage = {
          input_tokens: chunk.usageMetadata.promptTokenCount || 0,
          output_tokens: chunk.usageMetadata.candidatesTokenCount || 0,
        };
      }
    }
  }

  flushTextBlock();

  // Mappa finishReason Gemini → stop_reason canonico
  let stopReason = "end_turn";
  if (accContent.some(b => b.type === "tool_use")) stopReason = "tool_use";
  else if (finishReason === "MAX_TOKENS") stopReason = "max_tokens";
  else if (finishReason === "STOP") stopReason = "end_turn";

  yield { type: "stop", stop_reason: stopReason, usage, content: accContent };
}

// =============================================================
// Error parsing
// =============================================================
function parseProviderError(provider, status, body) {
  let parsed;
  try { parsed = JSON.parse(body); } catch { parsed = null; }

  // Anthropic credit check
  if (provider === "anthropic" && parsed?.error?.message?.includes("credit balance")) {
    return "💳 Credito Anthropic esaurito. Aggiungi fondi su console.anthropic.com → Plans & Billing, oppure passa a Gemini (gratis) dal pulsante AI in alto.";
  }
  if (provider === "anthropic" && status === 401) {
    return "🔑 API key Anthropic non valida. Controllala su console.anthropic.com → API Keys.";
  }
  if (provider === "gemini" && parsed?.error?.message) {
    if (parsed.error.message.includes("API key not valid")) {
      return "🔑 API key Gemini non valida. Crea una key gratis su aistudio.google.com/app/apikey.";
    }
    if (status === 429) {
      return "⏱️ Limite di richieste Gemini raggiunto temporaneamente (15/min, 1500/giorno sul tier gratis). Aspetta un attimo e riprova.";
    }
    if (status === 503 || /high demand|overload|unavailable/i.test(parsed.error.message)) {
      return "⏳ Server Gemini sovraccarico (HTTP 503) — non è un tuo errore, è Google. Suggerimenti: 1) aspetta 30-60s e riprova, 2) prova l'altro modello Gemini dalla tendina, 3) se hai credito Claude, passa a Anthropic dal pulsante in alto.";
    }
    return `Errore Gemini: ${parsed.error.message}`;
  }

  const msg = parsed?.error?.message || body.slice(0, 300);
  return `HTTP ${status}: ${msg}`;
}

// =============================================================
// Unified dispatcher
// =============================================================
async function* streamAI(options) {
  const active = getActive();
  if (!active.key) {
    yield { type: "error", message: "Nessuna API key impostata. Apri il modal in alto a destra." };
    return;
  }

  // Adatta il modello al provider attivo se non specificato o specificato sull'altro
  let model = options.model;
  const validModelIds = active.info.models.map(m => m.id);
  if (!model || !validModelIds.includes(model)) {
    model = active.info.models.find(m => m.default)?.id || active.info.models[0].id;
  }

  const adjOptions = { ...options, model };

  if (active.name === "anthropic") {
    yield* streamAnthropic(active.key, adjOptions);
  } else if (active.name === "gemini") {
    yield* streamGemini(active.key, adjOptions);
  } else {
    yield { type: "error", message: `Provider sconosciuto: ${active.name}` };
  }
}

window.AI = {
  providers: PROVIDERS,
  getActive,
  setActive,
  getKey,
  setKey,
  hasValidActive,
  streamAI,
};
