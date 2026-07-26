import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { ChatResponse } from "../types";

interface Msg {
  role: "user" | "ai";
  text: string;
}

export default function AIChat() {
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(true);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!collapsed && bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight;
    }
  }, [messages, collapsed]);

  if (!user) return null;

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setLoading(true);
    try {
      const res = await api.post<ChatResponse>("/api/ai/chat", { message: text, language });
      setMessages((prev) => [...prev, { role: "ai", text: res.reply }]);
    } catch {
      setMessages((prev) => [...prev, { role: "ai", text: "Sorry, I couldn't reach the AI service. Please try again." }]);
    } finally {
      setLoading(false);
    }
  }

  async function switchLanguage(lang: string) {
    setLanguage(lang);
    setMessages((prev) => [...prev, { role: "user", text: `Switched language to ${lang.toUpperCase()}` }]);
    setLoading(true);
    try {
      const res = await api.post<ChatResponse>("/api/ai/chat", { message: "hello", language: lang });
      setMessages((prev) => [...prev, { role: "ai", text: res.reply }]);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  if (collapsed) {
    return (
      <div className="chat-panel collapsed" onClick={() => setCollapsed(false)}>
        <div className="chat-header" style={{ border: "none", padding: "0.6rem 1.2rem" }}>
          AI Assistant
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span>AI Assistant</span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <select
            value={language}
            onChange={(e) => switchLanguage(e.target.value)}
            style={{ width: "auto", padding: "0.2rem 0.4rem", minHeight: "auto", fontSize: "0.75rem", borderRadius: 6 }}
          >
            <option value="en">EN</option>
            <option value="zh">中文</option>
            <option value="ms">BM</option>
            <option value="ta">தமிழ்</option>
          </select>
          <button
            onClick={() => setCollapsed(true)}
            style={{ background: "none", border: "none", cursor: "pointer", color: "var(--ink-500)", fontSize: "1.1rem" }}
          >
            x
          </button>
        </div>
      </div>

      <div className="chat-body" ref={bodyRef}>
        {messages.length === 0 && (
          <div className="chat-bubble ai">
            Hi! I'm your AI assistant. Ask me about events, learning journeys, or growth plans.
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`chat-bubble ${m.role}`}>
            {m.text}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble ai" style={{ opacity: 0.7 }}>
            Thinking...
          </div>
        )}
      </div>

      <div className="chat-input-row">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask anything..."
          style={{ flex: 1, minHeight: "auto", padding: "0.5rem 0.7rem", fontSize: "0.88rem" }}
        />
        <button className="btn btn-primary btn-sm" onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
