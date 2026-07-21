from langgraph.graph import StateGraph, START, END

from app.workflows.langgraph.state import AgentState
from app.workflows.langgraph.nodes import (
    query_understanding_node,
    retrieval_node,
    context_evaluation_node,
    query_rewrite_node,
    response_generation_node,
    reflection_node,
    evidence_verification_node,
    citation_node,
    refusal_node
)
from app.workflows.langgraph.router import (
    route_after_intent,
    route_after_context_evaluation,
    route_after_verification
)


def create_agent_graph() -> StateGraph:
    """Creates and compiles the self-correcting RAG workflow graph."""
    workflow = StateGraph(AgentState)

    # 1. Define Nodes
    workflow.add_node("query_understanding", query_understanding_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("context_evaluation", context_evaluation_node)
    workflow.add_node("query_rewrite", query_rewrite_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("reflection", reflection_node)
    workflow.add_node("evidence_verification", evidence_verification_node)
    workflow.add_node("citation_agent", citation_node)
    workflow.add_node("refusal", refusal_node)

    # 2. Add Flow Edges
    
    # Entrance
    workflow.add_edge(START, "query_understanding")
    
    # Post-Intent classification conditional routing
    workflow.add_conditional_edges(
        "query_understanding",
        route_after_intent,
        {
            "retrieval": "retrieval",
            "refusal": "refusal"
        }
    )
    
    # Retrieval flows directly to Context Evaluation
    workflow.add_edge("retrieval", "context_evaluation")
    
    # Post-Context evaluation conditional routing (checks relevance / loops)
    workflow.add_conditional_edges(
        "context_evaluation",
        route_after_context_evaluation,
        {
            "query_rewrite": "query_rewrite",
            "response_generation": "response_generation",
            "refusal": "refusal"
        }
    )
    
    # Query rewrite loops back to Retrieval
    workflow.add_edge("query_rewrite", "retrieval")
    
    # Generation flows through Reflection to Evidence Verification
    workflow.add_edge("response_generation", "reflection")
    workflow.add_edge("reflection", "evidence_verification")
    
    # Post-Verification conditional routing (checks factual alignment / retry loops)
    workflow.add_conditional_edges(
        "evidence_verification",
        route_after_verification,
        {
            "citation_agent": "citation_agent",
            "response_generation": "response_generation",
            "refusal": "refusal"
        }
    )
    
    # Final terminals
    workflow.add_edge("citation_agent", END)
    workflow.add_edge("refusal", END)

    # Compile the graph
    return workflow.compile()


# Export compiled graph singleton
app_graph = create_agent_graph()
