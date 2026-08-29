"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import { DEFAULT_PERSONA } from "../../lib/persona";
import { loadPersona, loadMessages, saveMessages } from "../../lib/storage";
import { fetchReply } from "../../lib/api";
import { pickBestVoice } from "../../lib/voices";
import { speakWithElevenLabs, transcribeAudio } from "../../lib/elevenlabs";
import { createRecorder, isRecordingSupported } from "../../lib/recorder";

const STATUS = {
  IDLE: "idle",
  READY: "ready", // call active, waiting for the user to hold the talk button
  RECORDING: "recording",
  TRANSCRIBING: "transcribing",
  THINKING: "thinking",
  SPEAKING: "speaking",
  ENDED: "ended",
};

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
    .toString()
    .padStart(2, "0");
  const s = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${m}:${s}`;
}

export default function CallPage() {
  const [persona, setPersona] = useState(DEFAULT_PERSONA);
  const [status, setStatus] = useState(STATUS.IDLE);
  const [supported, setSupported] = useState(true);
  const [error, setError] = useState("");
  const [transcriptLine, setTranscriptLine] = useState("");
  const [elapsed, setElapsed] = useState(0);

  const historyRef = useRef([]);
  const activeRef = useRef(false);
  const timerRef = useRef(null);
  const voicesRef = useRef([]);
  const recorderRef = useRef(null);

  useEffect(() => {
    setPersona(loadPersona(DEFAULT_PERSONA));
    historyRef.current = loadMessages();
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!isRecordingSupported() || !("speechSynthesis" in window)) {
      setSupported(false);
      return;
    }
    recorderRef.current = createRecorder();

    function loadVoices() {
      voicesRef.current = window.speechSynthesis.getVoices();
    }
    loadVoices();
    window.speechSynthesis.addEventListener("voiceschanged", loadVoices);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", loadVoices);
  }, []);

  const speakWithBrowser = useCallback(
    (text) =>
      new Promise((resolve) => {
        if (typeof window === "undefined" || !("speechSynthesis" in window)) {
          resolve();
          return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        const voice =
          voicesRef.current.find((v) => v.voiceURI === persona.voiceURI) ||
          pickBestVoice(voicesRef.current);
        if (voice) utterance.voice = voice;
        utterance.onend = resolve;
        utterance.onerror = resolve;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
      }),
    [persona.voiceURI]
  );

  const speak = useCallback(
    async (text) => {
      if (persona.ttsProvider === "elevenlabs" && persona.elevenlabsVoiceId) {
        try {
          await speakWithElevenLabs(text, persona.elevenlabsVoiceId);
          return;
        } catch (err) {
          console.error("ElevenLabs playback failed, falling back to browser voice:", err);
          setError("ElevenLabs voice failed, used browser voice instead: " + (err.message || ""));
        }
      }
      await speakWithBrowser(text);
    },
    [persona.ttsProvider, persona.elevenlabsVoiceId, speakWithBrowser]
  );

  async function startCall() {
    setError("");
    try {
      await recorderRef.current.requestPermission();
    } catch (err) {
      setError("Microphone access is needed for calls. " + (err.message || ""));
      return;
    }
    activeRef.current = true;
    setStatus(STATUS.READY);
    setElapsed(0);
    timerRef.current = setInterval(() => setElapsed((s) => s + 1), 1000);
  }

  function endCall() {
    activeRef.current = false;
    window.speechSynthesis?.cancel();
    recorderRef.current?.release();
    clearInterval(timerRef.current);
    setStatus(STATUS.ENDED);
  }

  useEffect(() => {
    return () => {
      activeRef.current = false;
      recorderRef.current?.release();
      if (typeof window !== "undefined") window.speechSynthesis?.cancel();
      clearInterval(timerRef.current);
    };
  }, []);

  async function handleTalkStart() {
    if (status !== STATUS.READY) return;
    setError("");
    setTranscriptLine("");
    try {
      await recorderRef.current.start();
      setStatus(STATUS.RECORDING);
    } catch (err) {
      setError("Couldn't start recording. " + (err.message || ""));
    }
  }

  async function handleTalkEnd() {
    if (status !== STATUS.RECORDING) return;

    setStatus(STATUS.TRANSCRIBING);
    let blob;
    try {
      blob = await recorderRef.current.stop();
    } catch (err) {
      setError(err.message || "Recording failed");
      setStatus(STATUS.READY);
      return;
    }

    let said = "";
    try {
      said = await transcribeAudio(blob);
    } catch (err) {
      setError(err.message || "Transcription failed");
      setStatus(STATUS.READY);
      return;
    }

    if (!activeRef.current) return;
    if (!said.trim()) {
      setStatus(STATUS.READY);
      return;
    }
    setTranscriptLine(said);

    const next = [...historyRef.current, { role: "user", content: said }];
    historyRef.current = next;
    saveMessages(next);

    setStatus(STATUS.THINKING);
    let reply = "";
    try {
      reply = await fetchReply({ messages: next, persona, mode: "call" });
    } catch (err) {
      setError(err.message || "Something went wrong");
      setStatus(STATUS.READY);
      return;
    }
    if (!activeRef.current) return;

    const withReply = [...historyRef.current, { role: "assistant", content: reply }];
    historyRef.current = withReply;
    saveMessages(withReply);

    setStatus(STATUS.SPEAKING);
    setTranscriptLine(reply);
    await speak(reply);
    if (activeRef.current) setStatus(STATUS.READY);
  }

  const statusLabel =
    {
      [STATUS.IDLE]: "Ready to call",
      [STATUS.READY]: "Hold the button to talk",
      [STATUS.RECORDING]: "Listening… release when done",
      [STATUS.TRANSCRIBING]: "…",
      [STATUS.THINKING]: "…",
      [STATUS.SPEAKING]: `${persona.name} is talking…`,
      [STATUS.ENDED]: "Call ended",
    }[status] || "";

  const inCall = status !== STATUS.IDLE && status !== STATUS.ENDED;
  const busy = status === STATUS.TRANSCRIBING || status === STATUS.THINKING || status === STATUS.SPEAKING;

  return (
    <div className="mx-auto flex h-screen max-w-lg flex-col items-center justify-between bg-gradient-to-b from-fuchsia-900 via-indigo-900 to-slate-950 px-6 py-10">
      <div className="w-full">
        <Link href="/" className="text-sm text-white/40">
          ‹ Back to texts
        </Link>
      </div>

      <div className="flex flex-col items-center gap-4">
        <div className="relative flex h-32 w-32 items-center justify-center">
          {status === STATUS.RECORDING && (
            <span className="absolute inset-0 rounded-full bg-green-500/40 animate-pulseRing" />
          )}
          {status === STATUS.SPEAKING && (
            <span className="absolute inset-0 rounded-full bg-imessage-blue/40 animate-pulseRing" />
          )}
          {persona.avatar ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={persona.avatar}
              alt={persona.name}
              className="relative h-28 w-28 rounded-full object-cover"
            />
          ) : (
            <div className="relative flex h-28 w-28 items-center justify-center rounded-full bg-white/10 text-3xl font-semibold">
              {persona.name?.[0]?.toUpperCase() || "?"}
            </div>
          )}
        </div>
        <div className="text-xl font-semibold">{persona.name}</div>
        <div className="text-sm text-white/50">{statusLabel}</div>
        {inCall && <div className="text-xs text-white/30">{formatDuration(elapsed)}</div>}
        {transcriptLine && (
          <p className="max-w-xs text-center text-sm text-white/70">{transcriptLine}</p>
        )}
        {error && <p className="max-w-xs text-center text-sm text-red-400">{error}</p>}
        {!supported && (
          <p className="max-w-xs text-center text-sm text-yellow-400">
            Voice calling needs microphone and audio support, which this browser doesn't
            provide — you can still text instead.
          </p>
        )}
      </div>

      <div className="flex flex-col items-center gap-4 pb-6">
        {!inCall ? (
          <button
            onClick={startCall}
            disabled={!supported}
            className="flex h-16 w-16 items-center justify-center rounded-full bg-green-500 text-2xl disabled:opacity-30"
            aria-label="Start call"
          >
            📞
          </button>
        ) : (
          <>
            <button
              onPointerDown={handleTalkStart}
              onPointerUp={handleTalkEnd}
              onPointerLeave={() => status === STATUS.RECORDING && handleTalkEnd()}
              disabled={busy}
              className={`flex h-24 w-24 select-none items-center justify-center rounded-full text-3xl transition-colors disabled:opacity-30 ${
                status === STATUS.RECORDING ? "bg-green-500" : "bg-white/10"
              }`}
              aria-label="Hold to talk"
            >
              🎙️
            </button>
            <button
              onClick={endCall}
              className="flex h-14 w-14 items-center justify-center rounded-full bg-red-500 text-xl"
              aria-label="End call"
            >
              ✕
            </button>
          </>
        )}
      </div>
    </div>
  );
}
