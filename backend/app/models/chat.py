from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class ChatSession(Base):
    id = Column(String, primary_key=True, index=True) # UUID string format
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_session.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(String, nullable=False)
    
    # Metadata & Evaluation
    citations = Column(JSON, nullable=True) # citations/references array
    confidence_score = Column(Float, nullable=True) # numeric overall confidence
    metadata_json = Column(JSON, nullable=True) # detailed breakdowns, execution latency, models
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    feedbacks = relationship("Feedback", back_populates="message", cascade="all, delete-orphan")
