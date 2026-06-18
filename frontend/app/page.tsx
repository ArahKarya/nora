"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import ChatPanel from "@/components/ChatPanel";
import SourcesPanel from "@/components/SourcesPanel";
import {
  me,
  getTopics,
  logout,
  ApiError,
  type User,
  type Topic,
  type QueryResult,
} from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [panelOpen, setPanelOpen] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const u = await me();
        setUser(u);
        const ts = await getTopics();
        setTopics(ts);
        if (ts.length > 0) setActiveId(ts[0].id);
      } catch (e) {
        if (e instanceof ApiError && e.status === 401) {
          router.replace("/login");
          return;
        }
        // network/backend down: tetap render shell kosong
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleLogout() {
    try {
      await logout();
    } catch {
      /* ignore */
    }
    router.replace("/login");
  }

  const activeTopic = topics.find((t) => t.id === activeId) ?? null;

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-offwhite font-mono text-xs uppercase tracking-wide text-slate-400">
        Memuat…
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <Sidebar
        topics={topics}
        activeId={activeId}
        onSelect={setActiveId}
        user={user}
        onLogout={handleLogout}
      />
      <ChatPanel topic={activeTopic} onResult={setResult} />
      <SourcesPanel
        result={result}
        open={panelOpen}
        onToggle={() => setPanelOpen((v) => !v)}
      />
    </div>
  );
}
