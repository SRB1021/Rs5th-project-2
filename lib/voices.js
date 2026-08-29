// Browser TTS voice quality varies wildly by OS/browser. This scores the
// available voices so we can default to the most natural-sounding American
// English one instead of whatever the OS happens to list first (often a
// dated, robotic-sounding voice).

const GOOD_NAME_HINTS = [
  "natural", // Edge/Windows neural voices, e.g. "Microsoft Ava Online (Natural)"
  "online",
  "premium",
  "enhanced",
  "neural",
  "google us english",
  "samantha", // macOS
  "ava",
  "nova",
  "aria",
];

const BAD_NAME_HINTS = [
  "espeak",
  "compact", // older, lower-quality mobile voices
  "desktop", // legacy Microsoft SAPI voices (David/Zira Desktop) — dated and robotic
];

function score(voice) {
  const name = voice.name.toLowerCase();
  const isUSEnglish = voice.lang?.toLowerCase() === "en-us";
  const isEnglish = voice.lang?.toLowerCase().startsWith("en");

  let s = 0;
  if (isUSEnglish) s += 10;
  else if (isEnglish) s += 3;

  if (GOOD_NAME_HINTS.some((hint) => name.includes(hint))) s += 8;
  if (BAD_NAME_HINTS.some((hint) => name.includes(hint))) s -= 8;
  if (voice.localService === false) s += 1; // network voices tend to sound better

  return s;
}

export function pickBestVoice(voices) {
  if (!voices || voices.length === 0) return null;
  return [...voices].sort((a, b) => score(b) - score(a))[0];
}

export function sortVoicesByQuality(voices) {
  return [...voices].sort((a, b) => score(b) - score(a));
}
