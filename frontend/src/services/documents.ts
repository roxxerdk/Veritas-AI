import api from "./api";
import { Document, IngestionStatus } from "../types";

export const documentsService = {
  async list(): Promise<Document[]> {
    const response = await api.get("/documents");
    return response.data;
  },

  async upload(file: File, onUploadProgress?: (progressEvent: any) => void): Promise<Document> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress,
    });
    return response.data;
  },

  async delete(documentId: number): Promise<void> {
    await api.delete(`/documents/${documentId}`);
  },

  async getStatus(documentId: number): Promise<IngestionStatus> {
    const response = await api.get(`/documents/${documentId}/status`);
    return response.data;
  }
};
