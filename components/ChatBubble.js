export default function ChatBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[75%] rounded-2xl px-4 py-2 text-[15px] leading-snug whitespace-pre-wrap break-words ${
          isUser
            ? "bg-imessage-blue text-white rounded-br-md"
            : "bg-imessage-gray text-black rounded-bl-md"
        }`}
      >
        {text}
      </div>
    </div>
  );
}
