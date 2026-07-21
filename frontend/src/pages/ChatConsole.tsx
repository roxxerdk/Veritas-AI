import React, { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Bot, User, ThumbsUp, ThumbsDown, Info } from "lucide-react";
import { Sidebar } from "../components/layout/Sidebar";
import { EvidencePanel } from "../components/chat/EvidencePanel";
import { chatService } from "../services/chat";
import { ChatMessage, Citation } from "../types";

export const ChatConsole: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  
  // Highlighted citation state
  const [highlightedIndex, setHighlightedIndex] = useState<number | null>(null);
  
  // Right panel states
  const [activeCitations, setActiveCitations] = useState<Citation[]>([]);
  const [activeTrace, setActiveTrace] = useState<string[]>([]);
  const [activeConfidence, setActiveConfidence] = useState<number | undefined>(undefined);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Intercept inline citation tags and format them as interactive click tags
  const renderMessageContent = (content: string) => {
    // Regex matching inline citations like [1], [2], etc.
    const pattern = /(\[\d+\])/g;
    const parts = content.split(pattern);

    return parts.map((part, i) => {
      const match = part.match(/^\[(\d+)\]$/);
      if (match) {
        const index = parseInt(match[1]);
        return (
          <button
            key={i}
            onClick={() => {
              setHighlightedIndex(index);
              // Auto-scroll the citation card in the sidebar into view
              const element = document.getElementById(`citation-card-${index}`);
              if (element) {
                element.scrollIntoView({ behavior: "smooth", block: "center" });
              }
            }}
            className="inline-flex items-center justify-center h-4 w-4 rounded bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/35 hover:text-indigo-300 text-[10px] font-bold mx-0.5 align-middle border border-indigo-500/30 transition-all font-mono"
          >
            {index}
          </button>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setHighlightedIndex(null);

    try {
      const result = await chatService.sendQuery(userMessage.content, sessionId);
      
      // Update session ID if it was created dynamically
      if (!sessionId && result.session_id) {
        setSessionId(result.session_id);
      }

      // Add assistant response message
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: result.answer,
        confidence_score: result.confidence_score,
        citations: result.citations,
        metadata_json: {
          execution_trace: result.execution_trace,
          refusal: false
        }
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Load current metrics into side evidence workspace
      setActiveCitations(result.citations || []);
      setActiveTrace(result.execution_trace || []);
      setActiveConfidence(result.confidence_score);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || "Failed to contact agents. Verify local Ollama is active.";
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: `Error: ${errorMsg}`,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex bg-slate-950 min-h-screen">
      <Sidebar />

      {/* Main Workspace Frame */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Center Panel (Chat thread) */}
        <div className="flex-1 flex flex-col justify-between h-screen p-8 max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-slate-800 pb-4 mb-4">
            <MessageSquare className="h-8 w-8 text-indigo-400 animate-pulse" />
            <div>
              <h1 className="text-xl font-bold text-slate-100">Knowledge Assistant</h1>
              <p className="text-xs text-slate-500 font-medium">Multi-agent orchestrator grounded in uploaded documentation.</p>
            </div>
          </div>

          {/* Messages list */}
          <div className="flex-1 overflow-y-auto pr-4 space-y-6 pb-6">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 py-16 gap-3">
                <Bot className="h-10 w-10 text-slate-700 animate-bounce" />
                <p className="text-sm font-semibold max-w-md">
                  I can answer your questions using the facts stored in your index library. Ask away!
                </p>
              </div>
            ) : (
              messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex gap-4 p-4 rounded-xl border ${
                    msg.role === "user"
                      ? "bg-slate-900/30 border-slate-800/80 self-end ml-16"
                      : "bg-slate-900/60 border-slate-800 self-start mr-16"
                  }`}
                >
                  {/* Icon */}
                  <div
                    className={`h-8 w-8 rounded-lg flex items-center justify-center border shrink-0 ${
                      msg.role === "user"
                        ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                        : "bg-purple-500/10 border-purple-500/20 text-purple-400"
                    }`}
                  >
                    {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>

                  {/* Message body */}
                  <div className="space-y-3 flex-1 overflow-hidden">
                    <p className="text-sm text-slate-300 leading-relaxed break-words whitespace-pre-line">
                      {msg.role === "user" ? msg.content : renderMessageContent(msg.content)}
                    </p>

                    {/* Feedback and verification details for assistant bubble */}
                    {msg.role === "assistant" && (
                      <div className="flex items-center justify-between border-t border-slate-800/40 pt-3 mt-1 text-xs text-slate-500">
                        <div className="flex items-center gap-1.5">
                          <button className="p-1 hover:text-slate-300 hover:bg-slate-800/40 rounded transition-all">
                            <ThumbsUp className="h-3.5 w-3.5" />
                          </button>
                          <button className="p-1 hover:text-slate-300 hover:bg-slate-800/40 rounded transition-all">
                            <ThumbsDown className="h-3.5 w-3.5" />
                          </button>
                        </div>
                        {msg.confidence_score !== undefined && (
                          <span className="font-mono text-[10px] font-semibold text-slate-500">
                            Confidence: {Math.round(msg.confidence_score * 100)}%
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {/* In-progress indicator */}
            {loading && (
              <div className="flex gap-4 p-4 rounded-xl border bg-slate-900/60 border-slate-800 self-start mr-16">
                <div className="h-8 w-8 rounded-lg flex items-center justify-center border bg-purple-500/10 border-purple-500/20 text-purple-400 shrink-0">
                  <Bot className="h-4 w-4 animate-spin" />
                </div>
                <div className="flex-1 space-y-2 py-1">
                  <div className="h-2.5 bg-slate-800 rounded w-1/4 animate-pulse"></div>
                  <div className="space-y-1.5">
                    <div className="h-2 bg-slate-800 rounded animate-pulse"></div>
                    <div className="h-2 bg-slate-800 rounded w-5/6 animate-pulse"></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Form Input query field */}
          <form onSubmit={handleSend} className="relative mt-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about the indexed knowledge base..."
              disabled={loading}
              className="w-full bg-slate-900/50 backdrop-blur-sm border border-slate-800 hover:border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 rounded-xl px-5 py-4 text-sm text-slate-300 pr-14 transition-all focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-2 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-800 text-slate-100 disabled:text-slate-600 rounded-lg transition-all"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>

        {/* Right Panel (Evidence Panel) */}
        <EvidencePanel
          citations={activeCitations}
          executionTrace={activeTrace}
          confidenceScore={activeConfidence}
          highlightedIndex={highlightedIndex}
        />
      </div>
    </div>
  );
};
