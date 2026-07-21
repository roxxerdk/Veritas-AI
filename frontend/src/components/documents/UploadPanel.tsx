import React, { useState, useRef } from "react";
import { Upload, FileText, AlertCircle, CheckCircle } from "lucide-react";
import { documentsService } from "../../services/documents";

interface UploadPanelProps {
  onUploadSuccess: () => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({ onUploadSuccess }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const uploadFile = async (file: File) => {
    // Validate file extension
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !["pdf", "docx", "txt", "md"].includes(ext)) {
      setError("Unsupported file format. Please upload PDF, DOCX, TXT, or MD.");
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);
    setSuccess(null);

    try {
      await documentsService.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percent);
      });
      setSuccess(`"${file.name}" uploaded successfully and added to indexing queue.`);
      onUploadSuccess();
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Upload failed. Verify file checksum is unique."
      );
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="glass-panel p-6">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Ingest Document</h3>
      
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all ${
          isDragActive
            ? "border-indigo-500 bg-indigo-500/5"
            : "border-slate-800 hover:border-slate-700 bg-slate-900/30 hover:bg-slate-900/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />

        <Upload className="h-10 w-10 text-indigo-400 mb-3 animate-pulse" />
        <p className="text-sm font-medium text-slate-300 text-center mb-1">
          {uploading ? "Uploading file..." : "Drag & drop file here, or click to browse"}
        </p>
        <p className="text-xs text-slate-500">PDF, DOCX, TXT, or MD up to 25MB</p>

        {uploading && (
          <div className="w-full mt-4 max-w-xs">
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Feedbacks */}
      {error && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg flex items-center gap-2">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mt-4 p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-lg flex items-center gap-2">
          <CheckCircle className="h-4 w-4 shrink-0" />
          <span>{success}</span>
        </div>
      )}
    </div>
  );
};
