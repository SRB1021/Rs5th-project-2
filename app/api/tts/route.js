export const runtime = "nodejs";

export async function POST(req) {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    return Response.json({ error: "ELEVENLABS_API_KEY is not set on the server" }, { status: 500 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return Response.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const { text, voiceId } = body || {};
  if (typeof text !== "string" || !text.trim()) {
    return Response.json({ error: "text is required" }, { status: 400 });
  }
  if (typeof voiceId !== "string" || !voiceId) {
    return Response.json({ error: "voiceId is required" }, { status: 400 });
  }

  const model = process.env.ELEVENLABS_MODEL || "eleven_turbo_v2_5";

  try {
    const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: "POST",
      headers: {
        "xi-api-key": apiKey,
        "Content-Type": "application/json",
        Accept: "audio/mpeg",
      },
      body: JSON.stringify({
        text: text.slice(0, 2000),
        model_id: model,
        voice_settings: { stability: 0.5, similarity_boost: 0.75 },
      }),
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      console.error("ElevenLabs TTS error:", res.status, detail);
      return Response.json(
        { error: `ElevenLabs request failed (${res.status})`, detail },
        { status: 502 }
      );
    }

    return new Response(res.body, {
      headers: { "Content-Type": "audio/mpeg" },
    });
  } catch (err) {
    console.error("ElevenLabs TTS error:", err);
    return Response.json({ error: "Failed to reach ElevenLabs" }, { status: 502 });
  }
}
