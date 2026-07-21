import React, { useEffect, useState } from "react";
import { Trash2, FileText, CheckCircle2, Clock, AlertTriangle, RefreshCw } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsService } from "../../services/documents";
import { Document } from "../../types";

interface StatusProgressProps {
  documentId: number;
  onComplete: () => void;
}

// Inline polling status component for documents currently indexing
const StatusProgress: React.FC<StatusProgressProps> = ({ documentId, onComplete }) => {
  const { data } = useQuery({
    queryKey: ["documentStatus", documentId],
    queryFn: () => documentsService.getStatus(documentId),
    refetchInterval: (query) => {
      // Poll every 2 seconds if status is not completed/failed
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") {
        onComplete();
        return false;
      }
      return 2000;
    },
  });

  if (!data) return <span className="text-slate-500">Initializing...</span>;

  // Formatting steps
  const statusColors: Record<string, string> = {
    queued: "text-amber-400 bg-amber-500/10 border-amber-500/20",
    parsing: "text-blue-400 bg-blue-500/10 border-blue-500/20",
    cleaning: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    chunking: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    embedding: "text-pink-400 bg-pink-500/10 border-pink-500/20",
    indexing: "text-teal-400 bg-teal-500/10 border-teal-500/20",
    failed: "text-red-400 bg-red-500/10 border-red-500/20",
    completed: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
  };

  const badgeColor = statusColors[data.status] || "text-slate-400 bg-slate-500/10 border-slate-500/20";

  return (
    <div className="flex flex-col gap-1 max-w-xs">
      <div className="flex items-center justify-between text-xs">
        <span className={`px-2 py-0.5 rounded-full border text-[10px] uppercase font-semibold ${badgeColor}`}>
          {data.status}
        </span>
        <span className="text-slate-400 font-mono font-medium">{data.progress}%</span>
      </div>
      <div className="w-24 bg-slate-800 rounded-full h-1 overflow-hidden">
        <div
          className="bg-indigo-500 h-1 rounded-full transition-all duration-300"
          style={{ width: `${data.progress}%` }}
        ></div>
      </div>
      <span className="text-[10px] text-slate-500 truncate">{data.current_step}</span>
    </div>
  );
};

export const ProcessingTable: React.FC = () => {
  const queryClient = useQueryClient();

  // List all user documents
  const { data: documents, isLoading, refetch } = useQuery({
    queryKey: ["documents"],
    queryFn: documentsService.list,
  });

  // Mutator for deleting a document
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentsService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
  });

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="glass-panel p-6 overflow-hidden">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-slate-200">Knowledge Inventory</h3>
        <button
          onClick={() => refetch()}
          className="p-2 text-slate-400 hover:text-slate-200 bg-slate-800/40 hover:bg-slate-800/80 rounded-lg border border-slate-800 transition-all"
        >
          <RefreshCw className="h-4 w-4" />
        </button>
      </div>

      {isLoading ? (
        <div className="py-12 flex justify-center text-sm text-slate-400">Loading documents...</div>
      ) : !documents || documents.length === 0 ? (
        <div className="py-16 text-center text-slate-500 flex flex-col items-center justify-center gap-3">
          <FileText className="h-8 w-8 text-slate-600" />
          <p className="text-sm">No documents indexed in knowledge base yet.</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800/60 text-slate-400 text-xs font-semibold uppercase tracking-wider">
                <th className="py-4 px-4">Filename</th>
                <th className="py-4 px-4">Type</th>
                <th className="py-4 px-4">Size</th>
                <th className="py-4 px-4">Status & Progress</th>
                <th className="py-4 px-4">Uploaded</th>
                <th className="py-4 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40 text-sm text-slate-300">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-900/20 transition-all">
                  <td className="py-4 px-4 font-medium flex items-center gap-2 max-w-xs truncate">
                    <FileText className="h-4 w-4 text-indigo-400 shrink-0" />
                    <span className="truncate">{doc.filename}</span>
                  </td>
                  <td className="py-4 px-4 text-xs font-mono text-slate-500">{doc.file_type}</td>
                  <td className="py-4 px-4 text-slate-400">{formatBytes(doc.file_size)}</td>
                  <td className="py-4 px-4">
                    {doc.status === "completed" ? (
                      <div className="flex items-center gap-2 text-emerald-400">
                        <CheckCircle2 className="h-4 w-4" />
                        <span className="text-xs">Indexed ({doc.page_count ?? 1} pages)</span>
                      </div>
                    ) : doc.status === "failed" ? (
                      <div className="flex items-center gap-2 text-red-400 text-xs">
                        <AlertTriangle className="h-4 w-4" />
                        <span>Failed</span>
                      </div>
                    ) : (
                      <StatusProgress
                        documentId={doc.id}
                        onComplete={() => queryClient.invalidateQueries({ queryKey: ["documents"] })}
                      />
                    )}
                  </td>
                  <td className="py-4 px-4 text-slate-500">{formatDate(doc.created_at)}</td>
                  <td className="py-4 px-4 text-right">
                    <button
                      onClick={() => deleteMutation.mutate(doc.id)}
                      disabled={deleteMutation.isPending}
                      className="p-1.5 text-red-500 hover:text-red-400 hover:bg-red-500/5 rounded-lg border border-transparent hover:border-red-500/10 transition-all"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
