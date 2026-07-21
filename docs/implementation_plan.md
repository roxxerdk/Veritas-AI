# Improvised Implementation Plan: LangGraph Self-Correcting Multi-Agent RAG

Build a production-quality, modular self-correcting RAG workflow using LangGraph and LangChain, orchestrated by seven specialized reasoning agents and a dedicated formatting agent.

---

## 1. Directory Structure

We will create the following files:

```text
backend/app/
│
├── prompts/
│   ├── query_understanding.txt
│   ├── context_evaluation.txt
│   ├── query_rewrite.txt
│   ├── response_generation.txt
│   ├── reflection.txt
│   └── evidence_verification.txt
│
├── services/
│   └── agents/
│       ├── base_agent.py
│       ├── query_understanding.py
│       ├── retrieval_agent.py
│       ├── context_evaluation.py
│       ├── query_rewrite.py
│       ├── response_generation.py
│       ├── reflection.py
│       ├── evidence_verification.py
│       └── citation_agent.py
│
└── workflows/
    └── langgraph/
        ├── state.py
        ├── nodes.py
        ├── router.py
        └── graph.py
```

---

## 2. Multi-Agent Graph Architecture (Improvised)

```text
                           User Query
                                │
                                ▼
                       [Understand Intent]
                                │
          ┌─────────────────────┴─────────────────────┐
     Out of Scope / Harmful                    In Scope & Valid
          │                                           │
          ▼                                           ▼
   [Refusal / Clarify]                     [Hybrid Retrieval (RRF)]
          │                                           │
          │                                           ▼
          │                                  [Evaluate Context]
          │                                           │
          │               ┌───────────────────────────┼───────────────────────────┐
          │      Context Sufficient          Context Poor (Loop < 2)     No Context (Loop >= 2)
          │               │                           │                           │
          │               ▼                           ▼                           ▼
          │       [Generate Answer]            [Rewrite Query]             [Refusal / Clarify]
          │               │                           │                           │
          │               ▼                           │                           │
          │           [Reflect] ◄─────────────────────┘                           │
          │               │                                                       │
          │               ▼                                                       │
          │     [Verify Against Evidence]                                         │
          │               │                                                       │
          │       ┌───────┴───────────────────────────┐                           │
          │    Verified                        Not Verified                       │
          │       │                                   │                           │
          │       ▼                                   ▼                           │
          │  [Citation Agent]             Retry (Loop < 2)?                       │
          │       │                        ├── Yes ──> [Generate Answer]          │
          │       │                        └── No  ──> [Refusal / Clarify]        │
          │       │                                           │                   │
          └───────┼───────────────────────────────────────────┴───────────────────┘
                  ▼
            Final Response
```

---

## 3. LangGraph State Schema (`workflows/langgraph/state.py`)

We define `AgentState` containing search targets, parsed payloads, feedback loops, and metrics:

```python
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
```

---

## 4. Agent Responsibilities & Structured Parsers

* **Base Agent (`base_agent.py`)**: Singleton Gemini LLM connector. Loads prompts dynamically from `app/prompts/` and implements automatic hot-reloading for developers.
* **Query Understanding Agent (`query_understanding.py`)**: Classifies intent, entities, and keywords. Output validated by Pydantic.
* **Retrieval Agent (`retrieval_agent.py`)**: Invokes database hybrid RRF retrieval (No LLM).
* **Context Evaluation Agent (`context_evaluation.py`)**: Grades relevance of each context chunk individually.
* **Query Rewrite Agent (`query_rewrite.py`)**: Reformulates query strings.
* **Response Generation Agent (`response_generation.py`)**: Synthesizes responses based *only* on approved chunks.
* **Reflection Agent (`reflection.py`)**: Inspects output for incompleteness and hallucinations.
* **Evidence Verification Agent (`evidence_verification.py`)**: Cross-references answer details against raw facts to output a numeric confidence rating.
* **Citation Agent (`citation_agent.py`)**: Maps source indices and formats citations (e.g. `[1] filename, page`).

---

## 5. Router Logic (`workflows/langgraph/router.py`)

Transitions:
1. `route_context`: Checks if `relevant_chunks` is populated. If empty and `rewrite_loop_count < 2`, route to `query_rewrite`. Otherwise, route to `response_generation` (if some chunks exist) or `refusal` (if no context is available).
2. `route_verification`: Evaluates verification outputs. If verified, routes to `citation_agent`. If failed and `reflection_loop_count < 2`, routes back to `response_generation` for a retry using feedback. Otherwise, routes to `refusal`.

---

## 6. Observability Metrics
Every node transition records latency, loop steps, and decisions to the `execution_trace` array to populate a detailed JSON response at the end of the query execution.
