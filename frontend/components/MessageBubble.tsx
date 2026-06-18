export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  pending?: boolean;
}

export default function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[75%] bg-navy px-4 py-3 text-sm leading-relaxed text-white"
            : "max-w-[75%] border border-slate-200 bg-white px-4 py-3 text-sm leading-relaxed text-ink"
        }
      >
        {!isUser && (
          <div className="mb-1 font-mono text-[10px] uppercase tracking-wide text-teal">
            NORA
          </div>
        )}
        <div className={`whitespace-pre-wrap ${msg.pending ? "opacity-50" : ""}`}>
          {msg.content || (msg.pending ? "…" : "")}
        </div>
      </div>
    </div>
  );
}
