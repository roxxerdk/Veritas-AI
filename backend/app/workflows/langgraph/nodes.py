import logging
import time
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from app.workflows.langgraph.state import AgentState
from app.services.agents.query_understanding import QueryUnderstandingAgent
from app.services.agents.retrieval_agent import RetrievalAgent
from app.services.agents.context_evaluation import ContextEvaluationAgent
from app.services.agents.query_rewrite import QueryRewriteAgent
from app.services.agents.response_generation import ResponseGenerationAgent
from app.services.agents.reflection import ReflectionAgent
from app.services.agents.evidence_verification import EvidenceVerificationAgent
from app.services.agents.citation_agent import CitationAgent

logger = logging.getLogger("veritas-ai.workflows.nodes")


def query_understanding_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = QueryUnderstandingAgent()
    result = agent.process_query(state["current_query"])
    latency = time.time() - start_time
    
    trace_msg = f"[Query Understanding] Intent: '{result['intent']}', Keywords: {result['keywords']} ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "intent": result["intent"],
        "entities": result["entities"],
        "search_keywords": result["keywords"],
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def retrieval_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    start_time = time.time()
    db = config.get("configurable", {}).get("db")
    if not db:
        raise ValueError("Database session missing from LangGraph config parameters.")
        
    agent = RetrievalAgent(db)
    # Search using combined search keywords, fallback to original query
    keywords = state.get("search_keywords", [])
    query_str = " ".join(keywords) if keywords else state["original_query"]
    chunks = agent.retrieve(query=query_str, top_k=5)
    
    # Fallback: if keyword search returned 0 hits, query using the full original query
    if not chunks and query_str != state["original_query"]:
        chunks = agent.retrieve(query=state["original_query"], top_k=5)
        
    latency = time.time() - start_time
    
    trace_msg = f"[Retrieval Agent] Fetched {len(chunks)} candidate text chunks from vector store ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "retrieved_chunks": chunks,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def context_evaluation_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = ContextEvaluationAgent()
    relevant = agent.evaluate_all(state["original_query"], state["retrieved_chunks"])
    latency = time.time() - start_time
    
    trace_msg = f"[Context Evaluation] Selected {len(relevant)}/{len(state['retrieved_chunks'])} relevant chunks ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "relevant_chunks": relevant,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def query_rewrite_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = QueryRewriteAgent()
    result = agent.rewrite_query(state["original_query"], state["current_query"])
    latency = time.time() - start_time
    
    new_loop = state.get("rewrite_loop_count", 0) + 1
    trace_msg = f"[Query Rewrite (Loop {new_loop})] Rewrote query to: '{result['rewritten_query']}' ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "current_query": result["rewritten_query"],
        "rewrite_loop_count": new_loop,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def response_generation_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = ResponseGenerationAgent()
    
    # Check if there is feedback from reflection loop
    feedback = state.get("reflection_feedback", "")
    
    answer = agent.generate_response(
        query=state["original_query"],
        relevant_chunks=state["relevant_chunks"],
        retry_feedback=feedback
    )
    latency = time.time() - start_time
    
    trace_msg = f"[Response Generation] Synthesized draft response ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "generated_answer": answer,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def reflection_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = ReflectionAgent()
    result = agent.reflect(
        query=state["original_query"],
        relevant_chunks=state["relevant_chunks"],
        answer=state["generated_answer"]
    )
    latency = time.time() - start_time
    
    trace_msg = f"[Reflection Agent] Complete: {result['complete']}, Hallucination: {result['hallucination']} ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "reflection_feedback": result["feedback"] if not result["complete"] or result["hallucination"] else "",
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def evidence_verification_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    # If reflection flagged problems, we don't verify and let the router loop back
    if state.get("reflection_feedback"):
        trace_msg = "[Evidence Verification] Skipped due to negative Reflection feedback."
        return {
            "execution_trace": state.get("execution_trace", []) + [trace_msg]
        }
        
    agent = EvidenceVerificationAgent()
    result = agent.verify(
        relevant_chunks=state["relevant_chunks"],
        answer=state["generated_answer"]
    )
    latency = time.time() - start_time
    
    new_loop = state.get("reflection_loop_count", 0)
    if not result["verified"]:
        new_loop += 1
        
    trace_msg = f"[Evidence Verification] Verified: {result['verified']}, Confidence: {result['confidence']:.2f} ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "confidence_score": result["confidence"],
        "verification_feedback": ", ".join(result["unsupported"]) if result["unsupported"] else "",
        "reflection_loop_count": new_loop,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def citation_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    agent = CitationAgent()
    formatted_answer, citations = agent.format_citations(
        answer=state["generated_answer"],
        relevant_chunks=state["relevant_chunks"]
    )
    latency = time.time() - start_time
    
    trace_msg = f"[Citation Agent] Mapped {len(citations)} source citations ({latency:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "generated_answer": formatted_answer,
        "citations": citations,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }


def refusal_node(state: AgentState) -> Dict[str, Any]:
    start_time = time.time()
    
    # Generate appropriate refusal message based on context evaluation or intent check
    if state.get("intent") == "out_of_scope":
        refusal_msg = "This query is out of scope or harmful. I can only assist you with questions related to uploaded documents."
    else:
        refusal_msg = "I'm sorry, but I couldn't find sufficient evidence in the uploaded documents to answer your question accurately."
        
    trace_msg = f"[Refusal Node] Rendered refusal message ({time.time() - start_time:.2f}s)"
    logger.info(trace_msg)
    
    return {
        "generated_answer": refusal_msg,
        "refusal": True,
        "execution_trace": state.get("execution_trace", []) + [trace_msg]
    }
