export default function TypingIndicator() {
  return (
    <div className="flex w-full justify-start">
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md bg-imessage-gray px-4 py-3">
        <span className="h-2 w-2 rounded-full bg-black/40 animate-bounce1 [animation-delay:0ms]" />
        <span className="h-2 w-2 rounded-full bg-black/40 animate-bounce1 [animation-delay:150ms]" />
        <span className="h-2 w-2 rounded-full bg-black/40 animate-bounce1 [animation-delay:300ms]" />
      </div>
    </div>
  );
}
