import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.workflows.langgraph.graph import app_graph

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: Any


class ChatResponse(BaseModel):
    session_id: str
    session_title: str
    answer: str
    confidence_score: float
    citations: List[Dict[str, Any]]
    execution_trace: List[str]


@router.post("/", response_model=ChatResponse)
async def process_chat_query(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Processes a user chat message using the self-correcting multi-agent RAG workflow."""
    # 1. Resolve or Create Chat Session
    session_id = request.session_id
    if session_id:
        chat_session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found or access denied."
            )
    else:
        # Create fresh session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            id=session_id,
            user_id=current_user.id,
            title=request.query[:30] + "..." if len(request.query) > 30 else request.query
        )
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

    # 2. Retrieve Chat History for LangGraph context
    history_messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    chat_history_list = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    # 3. Save User Message to Database
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.query
    )
    db.add(user_msg)
    db.commit()

    # 4. Invoke LangGraph Orchestrator
    initial_state = {
        "original_query": request.query,
        "current_query": request.query,
        "chat_history": chat_history_list,
        "intent": "",
        "entities": [],
        "search_keywords": [],
        "retrieved_chunks": [],
        "relevant_chunks": [],
        "generated_answer": "",
        "reflection_feedback": "",
        "verification_feedback": "",
        "verified_claims": [],
        "citations": [],
        "confidence_score": 1.0,
        "rewrite_loop_count": 0,
        "reflection_loop_count": 0,
        "refusal": False,
        "execution_trace": []
    }

    try:
        # Run graph providing active db session and authenticated user id via context variables
        config = {"configurable": {"db": db, "user_id": current_user.id}}
        final_state = app_graph.invoke(initial_state, config=config)
    except Exception as e:
        # Roll back and throw HTTP error if agent execution crashes
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent orchestrator failed to execute workflow: {str(e)}"
        )

    # 5. Save Assistant Answer to Database
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=final_state["generated_answer"],
        citations=final_state["citations"],
        confidence_score=final_state["confidence_score"],
        metadata_json={
            "execution_trace": final_state["execution_trace"],
            "refusal": final_state["refusal"]
        }
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        session_id=session_id,
        session_title=chat_session.title,
        answer=final_state["generated_answer"],
        confidence_score=final_state["confidence_score"],
        citations=final_state["citations"],
        execution_trace=final_state["execution_trace"]
    )
