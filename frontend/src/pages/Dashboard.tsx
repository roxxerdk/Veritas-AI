import React from "react";
import { useQuery } from "@tanstack/react-query";
import { LayoutDashboard, FileText, Cpu, Database, TrendingUp } from "lucide-react";
import { Sidebar } from "../components/layout/Sidebar";
import { UploadPanel } from "../components/documents/UploadPanel";
import { ProcessingTable } from "../components/documents/ProcessingTable";
import { documentsService } from "../services/documents";

export const Dashboard: React.FC = () => {
  const { data: documents, refetch } = useQuery({
    queryKey: ["documents"],
    queryFn: documentsService.list,
  });

  // Calculate high-level metrics from completed documents
  const stats = React.useMemo(() => {
    if (!documents) return { docsCount: 0, totalChunks: 0, avgLatency: "0.0s" };

    const completedDocs = documents.filter((d) => d.status === "completed");
    
    let chunkSum = 0;
    let latencySum = 0;
    let latencyCount = 0;

    completedDocs.forEach((doc: any) => {
      // Access structured metrics inside document metadata
      const metrics = doc.metadata_json?.ingestion_metrics;
      if (metrics) {
        chunkSum += metrics.chunk_count || 0;
        if (metrics.total_ingestion_time_sec) {
          latencySum += metrics.total_ingestion_time_sec;
          latencyCount++;
        }
      }
    });

    const average = latencyCount > 0 ? (latencySum / latencyCount).toFixed(2) : "0.00";

    return {
      docsCount: documents.length,
      totalChunks: chunkSum,
      avgLatency: `${average}s`,
    };
  }, [documents]);

  return (
    <div className="flex bg-slate-950 min-h-screen">
      <Sidebar />

      <main className="flex-1 p-8 space-y-8 overflow-y-auto">
        {/* Dashboard Header */}
        <div className="flex items-center gap-3">
          <LayoutDashboard className="h-8 w-8 text-indigo-400" />
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-100">Control Panel</h1>
            <p className="text-sm text-slate-400">Manage uploaded knowledge assets and monitoring pipelines.</p>
          </div>
        </div>

        {/* Dynamic Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="glass-panel p-6 flex items-center gap-4 hover:shadow-indigo-500/5 hover:border-slate-700 transition-all glow-indigo">
            <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400 border border-indigo-500/20">
              <FileText className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Indexed Documents</p>
              <h4 className="text-2xl font-bold text-slate-200 mt-1">{stats.docsCount}</h4>
            </div>
          </div>

          {/* Card 2 */}
          <div className="glass-panel p-6 flex items-center gap-4 hover:shadow-indigo-500/5 hover:border-slate-700 transition-all glow-indigo">
            <div className="p-3 bg-purple-500/10 rounded-xl text-purple-400 border border-purple-500/20">
              <Database className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Segment Chunks</p>
              <h4 className="text-2xl font-bold text-slate-200 mt-1">{stats.totalChunks} Chunks</h4>
            </div>
          </div>

          {/* Card 3 */}
          <div className="glass-panel p-6 flex items-center gap-4 hover:shadow-indigo-500/5 hover:border-slate-700 transition-all glow-indigo">
            <div className="p-3 bg-teal-500/10 rounded-xl text-teal-400 border border-teal-500/20">
              <TrendingUp className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Average Latency</p>
              <h4 className="text-2xl font-bold text-slate-200 mt-1">{stats.avgLatency}</h4>
            </div>
          </div>
        </div>

        {/* Dashboard Body Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload panel takes 1 column */}
          <div className="lg:col-span-1">
            <UploadPanel onUploadSuccess={() => refetch()} />
          </div>

          {/* Progress table takes 2 columns */}
          <div className="lg:col-span-2">
            <ProcessingTable />
          </div>
        </div>
      </main>
    </div>
  );
};
