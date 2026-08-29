export async function fetchVoices() {
  const res = await fetch("/api/tts/voices");
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `Failed to load voices (${res.status})`);
  return data.voices || [];
}

// Resolves once playback finishes. Throws if synthesis fails.
export async function speakWithElevenLabs(text, voiceId) {
  const res = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voiceId }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `Voice synthesis failed (${res.status})`);
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);

  await new Promise((resolve, reject) => {
    audio.onended = resolve;
    audio.onerror = () => reject(new Error("Playback failed"));
    audio.play().catch(reject);
  });

  URL.revokeObjectURL(url);
}

// Sends a recorded audio blob for transcription. Returns the transcript text.
export async function transcribeAudio(blob) {
  const form = new FormData();
  form.append("audio", blob, "recording.webm");

  const res = await fetch("/api/stt", { method: "POST", body: form });
  const data = await res.json().catch(() => ({}));

  if (!res.ok) throw new Error(data.error || `Transcription failed (${res.status})`);
  return data.text || "";
}
