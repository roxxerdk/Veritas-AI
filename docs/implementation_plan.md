# Improvised Implementation Plan: Ingestion & Hybrid Retrieval Services

Turn uploaded documents into searchable knowledge through an asynchronous pipeline (parsing -> cleaning -> chunking -> embedding -> indexing) and a modular hybrid retrieval system.

---

## 1. Directory Structure

```text
backend/app/services/
│
├── parsers/
│   ├── base_parser.py
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   ├── text_parser.py
│   ├── markdown_parser.py
│   └── parser_factory.py
│
├── preprocessing/
│   └── cleaner.py
│
├── chunking/
│   └── recursive_chunker.py
│
├── embeddings/
│   └── embedding_service.py
│
├── vectorstore/
│   └── qdrant_service.py
│
├── retrieval/
│   ├── semantic.py
│   ├── keyword.py
│   ├── rrf.py
│   └── retrieval_service.py
│
└── pipeline/
    └── ingestion_pipeline.py
```

---

## 2. Pipeline Phase Details & Improvisations

### Step 1 — Parsing (`parsers/`)
* Support PDF, DOCX, TXT, and Markdown.
* Implement a unified interface using `BaseParser` returning a structured `ParsedDocument` containing `text` (full body), `pages` (list of page indexes and text), and `metadata`.
* **Improvisation**: Graceful fallbacks in parser factory. If parsing fails, fall back to basic text decoding representation to prevent system crashes on corrupted formats.

### Step 2 — Cleaning (`preprocessing/`)
* **Improvisation**: Explicit cleaning rules:
  1. *Unicode Normalization*: Convert all characters to compatibility form (NFKC).
  2. *Whitespace Consolidation*: Replace consecutive spaces/tabs with single spaces, preserving double newlines for paragraph boundaries.
  3. *Ligature Resolution*: Translate ligatures (e.g., `ﬀ` -> `ff`, `ﬁ` -> `fi`) to ensure word matches.
  4. *Hyphen Joining*: Strip line-ending hyphens split by paragraph text wrapping.

### Step 3 — Chunking (`chunking/`)
* Split text character-wise using recursive splits: `["\n\n", "\n", " ", ""]`.
* Chunk sizes: **800–1000 characters** with an overlap of **100–150 characters**.

### Step 4 — Embeddings (`embeddings/`)
* Embedding Model: `BAAI/bge-small-en-v1.5` (384 dimensions).
* **Improvisation**: Thread-safe model caching. Load the SentenceTransformer model once on application startup as a global singleton.
* Expose `embed_documents(texts: List[str]) -> List[List[float]]` and `embed_query(text: str) -> List[float]`.

### Step 5 — Vector Store (`vectorstore/`)
* **Improvisation**: Auto-initialization. On start, inspect Qdrant for collection `veritas_chunks`. Create it dynamically using Cosine distance if absent.
* Upload payloads in batches of 32 for low-memory, fast HTTP operations.

### Step 6 — Hybrid Retrieval (`retrieval/`)
* **Semantic**: Fetches top-k dense vector candidates from Qdrant.
* **Keyword**: Lexical matcher (queries Qdrant payload text-search index).
* **RRF**: Merges matches using Reciprocal Rank Fusion:
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{60 + r_m(d)}$$
  Where $r_m(d)$ is the rank of document $d$ in system $m$.

### Step 7 — Asynchronous Background Ingestion (`pipeline/`)
* **Improvisation**: Triggered using FastAPI `BackgroundTasks`. The API immediately returns `202 Accepted` to free up the user interface.
* State transitions recorded in database: `queued` -> `parsing` -> `cleaning` -> `chunking` -> `embedding` -> `indexing` -> `completed`/`failed`.
* **Observability Ingestion Metrics**: Calculates and logs:
  - `parse_latency_sec`
  - `chunk_count`
  - `embedding_latency_sec`
  - `indexing_latency_sec`
  - `total_ingestion_time_sec`
  These are saved directly to `ProcessingJob` metadata or logs.

---

## 3. Verification Plan

* Upload a test document containing specific reference terms.
* Inspect database logs to ensure latencies and metadata are populated.
* Verify hybrid search API yields correct ranked results via test cases.
