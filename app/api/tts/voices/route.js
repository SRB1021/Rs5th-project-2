export const runtime = "nodejs";

function normalize(v) {
  return {
    voice_id: v.voice_id,
    name: v.name,
    category: v.category,
    gender: v.labels?.gender || null,
    accent: v.labels?.accent || null,
    description: v.labels?.description || null,
    preview_url: v.preview_url || null,
  };
}

export async function GET() {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  if (!apiKey) {
    return Response.json({ error: "ELEVENLABS_API_KEY is not set on the server" }, { status: 500 });
  }

  try {
    const [ownRes, sharedRes] = await Promise.all([
      fetch("https://api.elevenlabs.io/v1/voices", {
        headers: { "xi-api-key": apiKey },
      }),
      // Pull extra American-accented male voices from the shared voice
      // library so there's a real choice beyond the account's default set.
      fetch(
        "https://api.elevenlabs.io/v1/shared-voices?gender=male&accent=american&language=en&page_size=25",
        { headers: { "xi-api-key": apiKey } }
      ),
    ]);

    if (!ownRes.ok) {
      const detail = await ownRes.text().catch(() => "");
      return Response.json(
        { error: `ElevenLabs voices request failed (${ownRes.status})`, detail },
        { status: 502 }
      );
    }

    const ownData = await ownRes.json();
    const voices = (ownData.voices || []).map(normalize);

    if (sharedRes.ok) {
      const sharedData = await sharedRes.json();
      const seen = new Set(voices.map((v) => v.voice_id));
      for (const v of sharedData.voices || []) {
        if (!seen.has(v.voice_id)) {
          voices.push(normalize(v));
          seen.add(v.voice_id);
        }
      }
    }

    // Surface male voices first since the account's default premade set
    // tends to skew female.
    voices.sort((a, b) => {
      const aMale = a.gender === "male" ? 0 : 1;
      const bMale = b.gender === "male" ? 0 : 1;
      if (aMale !== bMale) return aMale - bMale;
      return a.name.localeCompare(b.name);
    });

    return Response.json({ voices });
  } catch (err) {
    console.error("ElevenLabs voices error:", err);
    return Response.json({ error: "Failed to reach ElevenLabs" }, { status: 502 });
  }
}
