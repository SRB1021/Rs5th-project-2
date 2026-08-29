import { textingSystemPrompt, callSystemPrompt } from "../../../lib/persona";

export const runtime = "nodejs";

function getApiKey() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("GEMINI_API_KEY is not set on the server");
  }
  return apiKey;
}

export async function POST(req) {
  let body;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const { messages, persona, mode } = body || {};

  if (!Array.isArray(messages) || messages.length === 0) {
    return Response.json({ error: "messages must be a non-empty array" }, { status: 400 });
  }
  if (!persona || typeof persona.name !== "string" || typeof persona.bio !== "string") {
    return Response.json({ error: "persona {name, bio} is required" }, { status: 400 });
  }

  const cleanMessages = messages
    .filter((m) => m && (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .map((m) => ({ role: m.role, content: m.content.slice(0, 8000) }))
    .slice(-40);

  if (cleanMessages.length === 0) {
    return Response.json({ error: "no valid messages" }, { status: 400 });
  }

  const system = mode === "call" ? callSystemPrompt(persona) : textingSystemPrompt(persona);
  const model = process.env.GEMINI_MODEL || "gemini-3.6-flash";

  let apiKey;
  try {
    apiKey = getApiKey();
  } catch (err) {
    return Response.json({ error: err.message }, { status: 500 });
  }

  const contents = cleanMessages.map((m) => ({
    role: m.role === "assistant" ? "model" : "user",
    parts: [{ text: m.content }],
  }));

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(apiKey)}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          system_instruction: { parts: [{ text: system }] },
          contents,
          generationConfig: { maxOutputTokens: 400 },
        }),
      }
    );

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      console.error("Gemini API error:", res.status, detail);
      return Response.json(
        { error: `Gemini request failed (${res.status})`, detail },
        { status: 502 }
      );
    }

    const data = await res.json();
    const text = (data.candidates?.[0]?.content?.parts || [])
      .map((p) => p.text || "")
      .join("\n")
      .trim();

    return Response.json({ text });
  } catch (err) {
    console.error("Gemini API error:", err);
    return Response.json({ error: "Failed to reach Gemini" }, { status: 502 });
  }
}
