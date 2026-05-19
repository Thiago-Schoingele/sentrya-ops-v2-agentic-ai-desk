# Sentrya Ops V2 — RAG Architecture Roadmap

Sentrya Ops V2 is currently designed as an agentic AI operations system with security, Telegram interface, LangGraph orchestration, LangSmith observability, multi-model routing, and administrative recovery controls.

This document defines the planned RAG layer for a future release.

The RAG layer is not active in the current version.

---

## 1. Current RAG Status

Current status:

```text
RAG planned
RAG not active in current release
Knowledge base placeholder created
Architecture documented
No vector database active yet
No embedding pipeline active yet
No retriever active yet
No Firecrawl integration active yet
```

Current placeholder file:

```text
data/knowledge_base.md
```

This file exists only as a future knowledge base placeholder.

---

## 2. Why RAG Will Be Added

The goal of the future RAG layer is to allow Sentrya Ops V2 to answer using controlled knowledge sources instead of relying only on the LLM internal knowledge.

The future RAG layer should help with:

- internal project documentation
- operational procedures
- service descriptions
- security policies
- recovery instructions
- client-specific FAQs
- technical runbooks
- integration documentation
- troubleshooting guides
- portfolio knowledge base
- commercial proposal knowledge

---

## 3. Planned RAG Use Cases

The future RAG layer may support:

```text
1. Answering questions about Sentrya Ops V2
2. Explaining the security architecture
3. Retrieving internal operational procedures
4. Assisting with client support workflows
5. Searching documentation before generating an answer
6. Supporting technical troubleshooting
7. Supporting commercial proposal generation
8. Supporting Upwork / portfolio-related answers
9. Supporting internal project memory
10. Supporting controlled business knowledge
```

---

## 4. Planned RAG Flow

The expected future flow:

```text
User message
        ↓
Operator Auth Gate
        ↓
Allowed Chat ID check
        ↓
Language Router
        ↓
Security Gate
        ↓
Lockdown Guard
        ↓
Intent classification
        ↓
RAG decision
        ↓
Retriever searches trusted knowledge base
        ↓
Relevant chunks returned
        ↓
LLM generates grounded answer
        ↓
Response returned in detected language
```

The RAG layer must always run after the Security Gate.

Unsafe input must never reach the retriever.

---

## 5. Planned RAG Architecture

Future components:

```text
data/knowledge_base.md
        ↓
Document loader
        ↓
Chunking strategy
        ↓
Embeddings
        ↓
Vector store
        ↓
Retriever
        ↓
RAG tool
        ↓
LangGraph node
        ↓
LLM response
```

Possible future files:

```text
src/rag_loader.py
src/rag_chunker.py
src/rag_retriever.py
src/rag_tool.py
tests/test_rag_pipeline.py
docs/rag_architecture.md
data/knowledge_base.md
```

These files are not active in the current release.

---

## 6. Possible Data Sources

The future RAG layer may be fed by:

### Internal project documents

```text
README.md
docs/security_architecture.md
docs/security_state_dashboard_contract.md
docs/rag_architecture.md
data/knowledge_base.md
```

### Operational documentation

```text
Telegram command guide
Recovery procedures
Lockdown procedures
Operator Auth guide
Security incident response guide
LangSmith metrics guide
```

### External collected knowledge

Possible future sources:

```text
Firecrawl crawled pages
client website content
FAQ pages
technical documentation
API documentation
approved public web pages
manual Markdown notes
```

External content must be cleaned, validated, and reviewed before entering the trusted knowledge base.

---

## 7. Firecrawl Role

Firecrawl may be used in the future to collect and structure web content for RAG.

Possible role:

```text
Website URL
        ↓
Firecrawl extraction
        ↓
Markdown / structured text
        ↓
Cleaning and filtering
        ↓
Human validation
        ↓
Knowledge base ingestion
        ↓
RAG retrieval
```

Firecrawl should not write directly into the production knowledge base without review.

Recommended rule:

```text
Firecrawl output must be reviewed before becoming trusted RAG knowledge.
```

---

## 8. Security Requirements for RAG

The future RAG layer must follow the same security principles as the rest of Sentrya Ops V2.

Rules:

```text
Security Gate runs before RAG
Unsafe input cannot trigger retrieval
Retrieved chunks must not expose secrets
Raw malicious payloads must not be stored
Private keys must not be indexed
.env files must never be indexed
Runtime logs must be sanitized before indexing
Telegram tokens must never be indexed
Operator Auth hash/salt must never be indexed
LangSmith private keys must never be indexed
Langflow private keys must never be indexed
```

The RAG layer must not ingest:

```text
.env
.venv/
__pycache__/
*.pyc
data/security_state.json
data/security_events.jsonl
credentials.json
token.json
secrets.json
private API keys
private tokens
```

---

## 9. RAG and Security State Machine

The RAG layer must respect the current security state.

Allowed states for RAG:

```text
NORMAL
RELEASED_MONITORING
```

Blocked states for RAG:

```text
LOCKDOWN
STAFF_ACTIVE
RECOVERY_PENDING
RECOVERY_VALIDATION
```

If the system is in a blocked state, the retriever must not run.

Expected behavior:

```text
System in LOCKDOWN
        ↓
User asks normal question
        ↓
Lockdown Guard blocks execution
        ↓
RAG does not run
```

---

## 10. RAG and Language Router

The RAG layer must preserve the user language.

Expected behavior:

```text
Portuguese input
        ↓
Portuguese retrieval context allowed
        ↓
Portuguese final answer
```

```text
English input
        ↓
English or multilingual retrieval context allowed
        ↓
English final answer
```

The final response must follow `detected_language` from `src/language_router.py`.

---

## 11. Planned Chunking Strategy

The future chunking strategy should prioritize semantic clarity.

Recommended initial chunking rules:

```text
Chunk by Markdown sections
Preserve headings
Keep security warnings with related content
Avoid splitting command blocks from explanations
Avoid very small fragments
Avoid very large chunks
Track source file and section title
```

Recommended metadata per chunk:

```json
{
  "source": "docs/security_architecture.md",
  "section": "Security Gate",
  "content_type": "documentation",
  "language": "en",
  "trusted": true
}
```

---

## 12. Planned Retrieval Strategy

Initial retrieval approach:

```text
User query
        ↓
Detect language
        ↓
Classify intent
        ↓
Search top relevant chunks
        ↓
Filter trusted sources
        ↓
Return compact context
        ↓
LLM answers using retrieved context
```

The LLM should be instructed:

```text
Use retrieved context when available.
Do not invent project-specific facts.
If the answer is not present in the knowledge base, say that the information is not available in the current project knowledge.
```

---

## 13. RAG Output Requirements

Future RAG answers must include:

```text
direct answer
source-aware reasoning
safe uncertainty when context is missing
language aligned with user input
no secrets
no raw internal keys
no hidden prompts
```

For public-facing responses, the answer should avoid exposing:

```text
internal file paths unless necessary
private operational details
raw event payloads
tokens
keys
hashes
security internals that could help attackers
```

---

## 14. Planned RAG Tool Contract

Future RAG tool input:

```json
{
  "query": "string",
  "language": "pt | en",
  "intent": "string",
  "max_chunks": 5
}
```

Future RAG tool output:

```json
{
  "status": "success",
  "query": "string",
  "chunks": [
    {
      "source": "string",
      "section": "string",
      "content": "string",
      "score": 0.0
    }
  ],
  "has_context": true
}
```

If no context is found:

```json
{
  "status": "no_context",
  "query": "string",
  "chunks": [],
  "has_context": false
}
```

---

## 15. Future Vector Store Options

Possible future vector stores:

```text
Chroma
FAISS
Qdrant
PostgreSQL + pgvector
```

Initial recommendation:

```text
Start with Chroma or FAISS locally for prototyping.
Use Qdrant or PostgreSQL + pgvector for production.
```

---

## 16. Future Embedding Options

Possible embedding providers:

```text
OpenAI embeddings
local embeddings
Hugging Face embeddings
Groq-compatible options if available
```

Selection criteria:

```text
cost
latency
quality
language support
Portuguese and English performance
deployment simplicity
privacy requirements
```

---

## 17. RAG and LangSmith

The future RAG layer should be observable in LangSmith.

Recommended trace metadata:

```json
{
  "rag_enabled": true,
  "retriever_used": true,
  "chunks_returned": 5,
  "knowledge_sources": ["docs/security_architecture.md"],
  "language": "en"
}
```

LangSmith should help monitor retrieval quality, latency, empty retrievals, token consumption, model behavior with retrieved context, hallucination risk, and error rate.

---

## 18. Future Tests

When RAG is implemented, tests should cover:

```text
document loading
chunk generation
metadata preservation
retriever response
empty context behavior
Portuguese query behavior
English query behavior
Security Gate before RAG
Lockdown blocks RAG
no secrets indexed
no .env indexed
```

Possible future test file:

```text
tests/test_rag_pipeline.py
```

---

## 19. Current Release Boundary

The current release does not activate RAG.

Current release focus:

```text
LangGraph agent
Groq multi-model routing
LangSmith observability
Telegram interface
Security Gate
Operator Auth Gate
Security State Machine
Lockdown Guard
Security Admin Command Layer
Telegram Admin Console
Language Router
72 automated tests
```

RAG is planned for a future iteration.

---

## 20. Roadmap

Recommended implementation order:

```text
1. Keep data/knowledge_base.md as placeholder
2. Document RAG architecture
3. Define approved knowledge sources
4. Build loader and chunker
5. Add embeddings
6. Add local vector store
7. Add retriever
8. Add RAG tool
9. Add LangGraph RAG node
10. Add tests
11. Add LangSmith tracing metadata
12. Add Dashboarder RAG visibility
```

---

## 21. Summary

The Sentrya Ops V2 project is now RAG-ready, but RAG is not active yet.

This keeps the current release stable while preparing the system for future knowledge-grounded responses.

Current status:

```text
RAG-ready architecture documented
Knowledge base placeholder created
No RAG runtime active
No new dependency added
No risk added to the current validated system
```
