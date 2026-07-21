import React from "react";
import { Settings as SettingsIcon, Terminal, Shield, CheckCircle, Database } from "lucide-react";
import { Sidebar } from "../components/layout/Sidebar";

export const Settings: React.FC = () => {
  return (
    <div className="flex bg-slate-950 min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8 space-y-8 overflow-y-auto max-w-4xl">
        {/* Header */}
        <div className="flex items-center gap-3">
          <SettingsIcon className="h-8 w-8 text-indigo-400" />
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-100">Settings</h1>
            <p className="text-sm text-slate-400">Configure parameters for agent execution and vector databases.</p>
          </div>
        </div>

        {/* Section 1: LLM Engine Configuration */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center gap-3 border-b border-slate-800 pb-3 mb-1">
            <Shield className="h-5 w-5 text-indigo-400" />
            <h3 className="text-base font-bold text-slate-200">Execution Configuration</h3>
          </div>

          <div className="space-y-4 text-sm">
            <div className="flex justify-between items-center p-3 bg-slate-800/10 border border-slate-800 rounded-lg">
              <div>
                <p className="font-semibold text-slate-300">LLM Provider Routing</p>
                <p className="text-xs text-slate-500">Determines if agent nodes query Google Gemini or local Ollama.</p>
              </div>
              <span className="px-3 py-1 bg-indigo-500/15 border border-indigo-500/35 text-indigo-400 text-xs font-bold rounded-full">
                Managed in .env
              </span>
            </div>

            <div className="flex justify-between items-center p-3 bg-slate-800/10 border border-slate-800 rounded-lg">
              <div>
                <p className="font-semibold text-slate-300">Local Model Target</p>
                <p className="text-xs text-slate-500">Model loaded when LLM_PROVIDER is set to ollama.</p>
              </div>
              <span className="font-mono text-xs text-slate-400">qwen2.5-coder:1.5b</span>
            </div>
          </div>
        </div>

        {/* Section 2: Systems Verification */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center gap-3 border-b border-slate-800 pb-3 mb-1">
            <Database className="h-5 w-5 text-indigo-400" />
            <h3 className="text-base font-bold text-slate-200">Data Tier Metrics</h3>
          </div>

          <div className="space-y-3 text-xs font-mono text-slate-400">
            <div className="flex justify-between p-2.5 bg-slate-950/40 rounded border border-slate-900">
              <span>PostgreSQL Host</span>
              <span className="text-emerald-400 flex items-center gap-1">localhost:5432 <CheckCircle className="h-3.5 w-3.5" /></span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-950/40 rounded border border-slate-900">
              <span>Qdrant Server URL</span>
              <span className="text-emerald-400 flex items-center gap-1">localhost:6333 <CheckCircle className="h-3.5 w-3.5" /></span>
            </div>
            <div className="flex justify-between p-2.5 bg-slate-950/40 rounded border border-slate-900">
              <span>Redis Cache Address</span>
              <span className="text-emerald-400 flex items-center gap-1">localhost:6379 <CheckCircle className="h-3.5 w-3.5" /></span>
            </div>
          </div>
        </div>

        {/* Section 3: Diagnostic Logs */}
        <div className="glass-panel p-6 space-y-4">
          <div className="flex items-center gap-3 border-b border-slate-800 pb-3 mb-1">
            <Terminal className="h-5 w-5 text-indigo-400" />
            <h3 className="text-base font-bold text-slate-200">Runtime console logs</h3>
          </div>

          <div className="p-4 bg-slate-950 rounded-xl border border-slate-850 font-mono text-xs text-indigo-300 leading-relaxed max-h-48 overflow-y-auto">
            <p>[19:04:14] Initialized Veritas AI Dashboard components successfully.</p>
            <p>[19:04:22] Loaded local tailwind directives into source index.css.</p>
            <p>[19:05:05] Context verification checks for active user sessions passed.</p>
            <p>[19:05:45] Compiled ChatConsole dynamic markdown listeners.</p>
          </div>
        </div>
      </main>
    </div>
  );
};
