export const runtime = "nodejs";

export async function POST(req) {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    return Response.json({ error: "ELEVENLABS_API_KEY is not set on the server" }, { status: 500 });
  }

  let incomingForm;
  try {
    incomingForm = await req.formData();
  } catch {
    return Response.json({ error: "Invalid form data" }, { status: 400 });
  }

  const audio = incomingForm.get("audio");
  if (!audio || typeof audio === "string") {
    return Response.json({ error: "audio file is required" }, { status: 400 });
  }

  const outgoingForm = new FormData();
  outgoingForm.append("file", audio, "recording.webm");
  outgoingForm.append("model_id", process.env.ELEVENLABS_STT_MODEL || "scribe_v1");

  try {
    const res = await fetch("https://api.elevenlabs.io/v1/speech-to-text", {
      method: "POST",
      headers: { "xi-api-key": apiKey },
      body: outgoingForm,
    });

    if (!res.ok) {
      const detail = await res.text().catch(() => "");
      console.error("ElevenLabs STT error:", res.status, detail);
      return Response.json(
        { error: `ElevenLabs transcription failed (${res.status})`, detail },
        { status: 502 }
      );
    }

    const data = await res.json();
    return Response.json({ text: data.text || "" });
  } catch (err) {
    console.error("ElevenLabs STT error:", err);
    return Response.json({ error: "Failed to reach ElevenLabs" }, { status: 502 });
  }
}
