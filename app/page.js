"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import ChatBubble from "../components/ChatBubble";
import TypingIndicator from "../components/TypingIndicator";
import MessageInput from "../components/MessageInput";
import { DEFAULT_PERSONA } from "../lib/persona";
import { loadMessages, saveMessages, loadPersona } from "../lib/storage";
import { fetchReply, splitBubbles } from "../lib/api";

export default function ChatPage() {
  const [persona, setPersona] = useState(DEFAULT_PERSONA);
  const [messages, setMessages] = useState([]);
  const [typing, setTyping] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    setPersona(loadPersona(DEFAULT_PERSONA));
    setMessages(loadMessages());
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  async function handleSend(text) {
    setError("");
    const userMsg = { role: "user", content: text };
    const next = [...messages, userMsg];
    setMessages(next);
    saveMessages(next);
    setTyping(true);

    try {
      const reply = await fetchReply({ messages: next, persona, mode: "text" });
      const bubbles = splitBubbles(reply);

      let running = next;
      for (let i = 0; i < bubbles.length; i++) {
        const delay = Math.min(1800, 400 + bubbles[i].length * 18);
        await new Promise((r) => setTimeout(r, delay));
        running = [...running, { role: "assistant", content: bubbles[i] }];
        setMessages(running);
        saveMessages(running);
      }
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setTyping(false);
    }
  }

  function handleClear() {
    if (!confirm(`Clear the entire text history with ${persona.name}?`)) return;
    setMessages([]);
    saveMessages([]);
  }

  return (
    <div className="mx-auto flex h-screen max-w-lg flex-col">
      <header className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <Link href="/settings" className="flex items-center gap-3">
          {persona.avatar ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={persona.avatar}
              alt={persona.name}
              className="h-9 w-9 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/10 text-sm font-semibold">
              {persona.name?.[0]?.toUpperCase() || "?"}
            </div>
          )}
          <div>
            <div className="text-sm font-semibold">{persona.name}</div>
            <div className="text-xs text-white/40">tap to edit profile</div>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <button
            onClick={handleClear}
            disabled={messages.length === 0}
            className="flex items-center gap-1 rounded-full bg-white/10 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-30"
            aria-label="Clear texts"
          >
            Clear
          </button>
          <Link
            href="/call"
            className="flex items-center gap-1 rounded-full bg-green-500 px-3 py-1.5 text-sm font-medium text-white"
          >
            Call
          </Link>
        </div>
      </header>

      <div className="flex-1 space-y-2 overflow-y-auto px-3 py-4">
        {messages.length === 0 && (
          <p className="mt-10 text-center text-sm text-white/30">
            Say hi to {persona.name}.
          </p>
        )}
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} text={m.content} />
        ))}
        {typing && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {error && <p className="px-4 pb-1 text-xs text-red-400">{error}</p>}

      <MessageInput onSend={handleSend} disabled={typing} />
    </div>
  );
}
