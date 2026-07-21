import api from "./api";
import { ChatMessage } from "../types";

export interface ChatResponsePayload {
  session_id: string;
  session_title: string;
  answer: string;
  confidence_score: number;
  citations: any[];
  execution_trace: string[];
}

export const chatService = {
  async sendQuery(query: string, sessionId?: string): Promise<ChatResponsePayload> {
    const response = await api.post("/chat", {
      query,
      session_id: sessionId
    });
    return response.data;
  }
};
