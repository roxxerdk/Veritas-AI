from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Feedback(Base):
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_message.id", ondelete="CASCADE"), nullable=False)
    is_positive = Column(Boolean, nullable=False) # true = thumbs up, false = thumbs down
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="feedbacks")
