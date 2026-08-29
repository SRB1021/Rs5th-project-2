# TextMate

Text an AI that replies like a real person, and call it for a live voice
conversation (audio only — no video).

## Features

- **Texting** — an iMessage-style chat where the AI persona replies casually,
  in short bursts of separate bubbles, with typing indicators. It's prompted
  to never sound like an assistant.
- **Calling** — tap Call, then hold the mic button to talk and release to
  send (push-to-talk). Your recording is transcribed via ElevenLabs, sent to
  the model, and the reply is spoken back out loud.
- **Editable profile** — tap the contact's name/photo in the chat header to
  change their name, personality/bio, profile picture, and call voice.
- **Natural voices (optional)** — switch the call voice engine to ElevenLabs
  in the profile editor for a realistic, human-sounding voice instead of the
  browser's built-in text-to-speech.

## Setup

```bash
npm install
cp .env.example .env.local   # then add your GEMINI_API_KEY and ELEVENLABS_API_KEY
npm run dev
```

Open http://localhost:3000. Get a free Gemini key at
https://aistudio.google.com/apikey (sign in with a Google account, no
credit card required), and a free ElevenLabs key at https://elevenlabs.io/
(Developers → API Keys — make sure the key has "Speech to Text" and
"Voices" permissions, not just Text to Speech).

`GEMINI_API_KEY` is required for texting and calling to work at all.
`ELEVENLABS_API_KEY` is required for **calling** specifically (it's used to
transcribe your voice) — texting works fine without it. Once it's set, the
call voice defaults to the browser's built-in voice; switch to "ElevenLabs
(natural)" in the profile editor for a more human-sounding reply voice too.

## Notes

- Voice calling uses `getUserMedia`/`MediaRecorder` to record your voice
  (widely supported, including Safari) and ElevenLabs to transcribe it —
  it does not rely on the browser's built-in `SpeechRecognition`, which is
  unreliable or missing in several browsers, Safari included.
- Text-to-speech (the AI's voice) uses ElevenLabs when configured, otherwise
  the browser's built-in `speechSynthesis`, auto-picking the best-sounding
  American English voice available.
- Conversation history and the persona/profile are stored in your browser's
  `localStorage` — nothing is saved server-side.
- This runs as a normal web app in a browser. It cannot be launched from
  Excel or any other office app.
