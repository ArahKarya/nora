"use client";

import { useEffect, useRef, useState } from "react";
import type { Topic, QueryResult } from "@/lib/api";
import { postQuery, ApiError } from "@/lib/api";
import MessageBubble, { ChatMessage } from "./MessageBubble";

export default function ChatPanel({
  topic,
  onResult,
}: {
  topic: Topic | null;
  onResult: (r: QueryResult | null) => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // reset thread saat ganti topik
  useEffect(() => {
    setMessages([]);
    setSessionId(undefined);
    setError(null);
    onResult(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [topic?.id]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function send() {
    const text = input.trim();
    if (!text || !topic || sending) return;
    setError(null);
    setInput("");
    setMessages((m) => [
      ...m,
      { role: "user", content: text },
      { role: "assistant", content: "", pending: true },
    ]);
    setSending(true);
    try {
      const res = await postQuery({
        topic_id: topic.id,
        message: text,
        session_id: sessionId,
      });
      setSessionId(res.session_id);
      onResult(res);
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = { role: "assistant", content: res.answer };
        return copy;
      });
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Gagal mengirim pertanyaan";
      setError(msg);
      setMessages((m) => m.slice(0, -1));
    } finally {
      setSending(false);
    }
  }

  function onKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <section className="flex h-full flex-1 flex-col bg-offwhite">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="font-bold uppercase tracking-wide text-navy">
          {topic?.name ?? "Pilih Topik"}
        </h1>
        {topic?.description && (
          <p className="mt-1 font-mono text-xs uppercase tracking-wide text-slate-400">
            {topic.description}
          </p>
        )}
      </header>

      <div className="scroll-thin flex-1 space-y-4 overflow-y-auto px-6 py-6">
        {messages.length === 0 && (
          <div className="mt-10 text-center font-mono text-xs uppercase tracking-wide text-slate-400">
            {topic
              ? "Ajukan pertanyaan tentang spesifikasi"
              : "Pilih topik di sebelah kiri untuk memulai"}
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} msg={m} />
        ))}
        <div ref={endRef} />
      </div>

      {error && (
        <div className="border-t border-conf-low/30 bg-conf-low/10 px-6 py-2 font-mono text-xs text-conf-low">
          {error}
        </div>
      )}

      <div className="border-t border-slate-200 bg-white px-6 py-4">
        <div className="flex items-end gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKey}
            disabled={!topic || sending}
            rows={2}
            placeholder={topic ? "Tulis pertanyaan…" : "Pilih topik dulu"}
            className="scroll-thin flex-1 resize-none border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none focus:border-navy disabled:bg-slate-50"
          />
          <button
            onClick={send}
            disabled={!topic || sending || !input.trim()}
            className="bg-teal px-5 py-3 font-mono text-xs font-bold uppercase tracking-wide text-white transition-opacity hover:opacity-90 disabled:opacity-40"
          >
            {sending ? "…" : "Kirim"}
          </button>
        </div>
      </div>
    </section>
  );
}
