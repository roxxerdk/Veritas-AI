from typing import Literal
from app.workflows.langgraph.state import AgentState


def route_after_intent(state: AgentState) -> Literal["retrieval", "refusal"]:
    """Routes to refusal immediately if intent is determined to be out of scope."""
    if state.get("intent") == "out_of_scope":
        return "refusal"
    return "retrieval"


def route_after_context_evaluation(
    state: AgentState
) -> Literal["query_rewrite", "response_generation", "refusal"]:
    """Routes based on context grading sufficiency and retry loops."""
    relevant_chunks = state.get("relevant_chunks", [])
    
    if not relevant_chunks:
        # Context is insufficient. Check loop limits for query rewrites.
        if state.get("rewrite_loop_count", 0) < 2:
            return "query_rewrite"
        return "refusal"
        
    return "response_generation"


def route_after_verification(
    state: AgentState
) -> Literal["citation_agent", "response_generation", "refusal"]:
    """Decides if the response can be finalized or needs self-correction iteration."""
    # Check if reflection or verification flagged issues
    has_reflection_feedback = bool(state.get("reflection_feedback"))
    has_verification_feedback = bool(state.get("verification_feedback"))
    
    # If no issues flagged, proceed to citations formatting
    if not has_reflection_feedback and not has_verification_feedback:
        return "citation_agent"
        
    # Check self-correction loop limits
    if state.get("reflection_loop_count", 0) < 2:
        return "response_generation"
        
    return "refusal"
