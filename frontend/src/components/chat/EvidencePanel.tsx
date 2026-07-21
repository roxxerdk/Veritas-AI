import React, { useState } from "react";
import { Info, CheckCircle, ShieldAlert, Sparkles, BookOpen, Clock } from "lucide-react";
import { Citation } from "../../types";

interface EvidencePanelProps {
  citations: Citation[];
  executionTrace: string[];
  confidenceScore?: number;
  highlightedIndex: number | null;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  citations,
  executionTrace,
  confidenceScore,
  highlightedIndex
}) => {
  const [activeTab, setActiveTab] = useState<"grounding" | "trace">("grounding");

  // Format confidence rating badge
  const getConfidenceBadge = (score: number) => {
    if (score >= 0.85) {
      return { text: "High Confidence", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" };
    } else if (score >= 0.6) {
      return { text: "Medium Confidence", color: "text-amber-400 bg-amber-500/10 border-amber-500/20" };
    }
    return { text: "Low Grounding", color: "text-red-400 bg-red-500/10 border-red-500/20" };
  };

  const confidenceBadge = confidenceScore !== undefined ? getConfidenceBadge(confidenceScore) : null;

  return (
    <div className="w-96 bg-slate-900/60 backdrop-blur-md border-l border-slate-800 flex flex-col h-screen sticky top-0">
      {/* Header Tabs */}
      <div className="flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab("grounding")}
          className={`flex-1 py-4 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 flex items-center justify-center gap-2 ${
            activeTab === "grounding"
              ? "text-indigo-400 border-indigo-500 bg-indigo-500/5"
              : "text-slate-500 border-transparent hover:text-slate-300"
          }`}
        >
          <BookOpen className="h-4 w-4" />
          Grounding Context
        </button>
        <button
          onClick={() => setActiveTab("trace")}
          className={`flex-1 py-4 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 flex items-center justify-center gap-2 ${
            activeTab === "trace"
              ? "text-indigo-400 border-indigo-500 bg-indigo-500/5"
              : "text-slate-500 border-transparent hover:text-slate-300"
          }`}
        >
          <Sparkles className="h-4 w-4" />
          System Trace
        </button>
      </div>

      {/* Workspace Panel Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {activeTab === "grounding" ? (
          <>
            {/* Confidence metric indicator */}
            {confidenceScore !== undefined && confidenceBadge && (
              <div className="flex items-center justify-between p-4 bg-slate-800/10 border border-slate-800 rounded-xl">
                <span className="text-xs text-slate-500 font-semibold uppercase">Verification Rating</span>
                <span className={`px-2.5 py-1 rounded-full border text-xs font-bold ${confidenceBadge.color}`}>
                  {confidenceBadge.text} ({Math.round(confidenceScore * 100)}%)
                </span>
              </div>
            )}

            {/* Citations List */}
            <div className="space-y-4">
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wide">Evidence Footnotes</h4>
              
              {citations.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
                  <Info className="h-5 w-5 text-slate-600" />
                  <span>Citations and source references will appear here.</span>
                </div>
              ) : (
                citations.map((c) => {
                  const isHighlighted = highlightedIndex === c.index;
                  
                  return (
                    <div
                      key={c.index}
                      id={`citation-card-${c.index}`}
                      className={`p-4 border rounded-xl transition-all duration-300 ${
                        isHighlighted
                          ? "bg-indigo-500/10 border-indigo-500 glow-indigo shadow-md"
                          : "bg-slate-800/20 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <span className="h-5 w-5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center text-xs font-bold font-mono">
                          {c.index}
                        </span>
                        <span className="text-xs font-bold text-slate-300 truncate max-w-[180px]">
                          {c.filename}
                        </span>
                        <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-400 shrink-0 font-semibold font-mono">
                          Page {c.page_number}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 italic leading-relaxed line-clamp-4 bg-slate-950/40 p-2.5 rounded border border-slate-900/60 font-mono">
                        "...{c.snippet}..."
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          </>
        ) : (
          /* System Execution trace node tree */
          <div className="space-y-4">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wide">LangGraph Flow Engine</h4>
            
            {executionTrace.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-500 flex flex-col items-center gap-2">
                <Clock className="h-5 w-5 text-slate-600 animate-spin" />
                <span>Execution path logs will compile during queries.</span>
              </div>
            ) : (
              <div className="relative border-l border-slate-800 pl-4 ml-2 space-y-6 py-2">
                {executionTrace.map((log, i) => {
                  const isSuccess = log.includes("Verified: True") || log.includes("Complete: True") || !log.includes("failed") && !log.includes("Error");
                  
                  return (
                    <div key={i} className="relative text-xs">
                      {/* Timeline dot */}
                      <span className="absolute -left-[21px] top-0.5 h-3.5 w-3.5 rounded-full border bg-slate-950 flex items-center justify-center">
                        <span className={`h-1.5 w-1.5 rounded-full ${isSuccess ? "bg-indigo-500" : "bg-red-500"}`}></span>
                      </span>
                      
                      <div className="bg-slate-900/40 border border-slate-900/80 p-3 rounded-lg flex flex-col gap-1 font-mono">
                        <p className="text-slate-300 text-[11px] leading-relaxed break-words">{log}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
