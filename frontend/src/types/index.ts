export interface User {
  id: number;
  email: string;
  is_active: boolean;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  page_count: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobMetrics {
  parse_latency_sec?: number;
  clean_latency_sec?: number;
  chunk_count?: number;
  chunk_latency_sec?: number;
  embedding_latency_sec?: number;
  indexing_latency_sec?: number;
  total_ingestion_time_sec?: number;
}

export interface IngestionStatus {
  document_id: number;
  status: string;
  progress: number;
  current_step: string;
  metrics: JobMetrics;
}

export interface Citation {
  index: number;
  filename: string;
  page_number: number;
  snippet: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  confidence_score?: number;
  citations?: Citation[];
  metadata_json?: {
    execution_trace: string[];
    refusal: boolean;
  };
  created_at?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}
