"use client";

import { useState } from "react";

export default function MessageInput({ onSend, disabled }) {
  const [value, setValue] = useState("");

  function submit(e) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  return (
    <form
      onSubmit={submit}
      className="flex items-center gap-2 border-t border-white/10 bg-black/30 p-3 backdrop-blur-md"
    >
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Text message"
        className="flex-1 rounded-full bg-white/10 px-4 py-2 text-[15px] text-white placeholder-white/40 outline-none focus:ring-2 focus:ring-imessage-blue"
        autoComplete="off"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="rounded-full bg-imessage-blue px-4 py-2 text-sm font-medium text-white disabled:opacity-30"
      >
        Send
      </button>
    </form>
  );
}
