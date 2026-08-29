export async function fetchReply({ messages, persona, mode }) {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, persona, mode }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data.error || `Request failed (${res.status})`;
    const detail = typeof data.detail === "string" ? data.detail.slice(0, 300) : "";
    throw new Error(detail ? `${message}: ${detail}` : message);
  }

  return data.text || "";
}

export function splitBubbles(text) {
  return text
    .split("|||")
    .map((s) => s.trim())
    .filter(Boolean);
}
