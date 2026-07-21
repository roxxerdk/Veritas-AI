from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: int
    chunk_index: int
    page_number: Optional[int]
    content: str
    token_count: int
    vector_id: Optional[str]

    class Config:
        from_attributes = True


class ProcessingJobResponse(BaseModel):
    id: int
    status: str
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    status: str
    page_count: Optional[int]
    language: str
    processing_error: Optional[str]
    uploaded_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    jobs: List[ProcessingJobResponse] = []

    class Config:
        from_attributes = True
