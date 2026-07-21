from typing import TypedDict, List, Dict, Any


class AgentState(TypedDict):
    original_query: str
    current_query: str
    chat_history: List[Dict[str, str]]
    
    # Query Analysis
    intent: str
    entities: List[str]
    search_keywords: List[str]
    
    # Context
    retrieved_chunks: List[Dict[str, Any]]
    relevant_chunks: List[Dict[str, Any]]
    
    # Responses & Evaluation
    generated_answer: str
    reflection_feedback: str
    verification_feedback: str
    verified_claims: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    confidence_score: float
    
    # Loop Counters
    rewrite_loop_count: int
    reflection_loop_count: int
    
    # Status Flags
    refusal: bool
    execution_trace: List[str]
