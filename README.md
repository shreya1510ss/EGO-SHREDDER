# Ego Shredder 🔥

AI chatbot that embodies Acharya Prashant's teaching style using RAG to ground responses in actual teachings from his book.

---

## What It Does

- **Responds as Acharya Prashant** — uncompromising, psychologically sharp, never coddling
- **Retrieves relevant teachings** from PDF via semantic search (RAG)
- **Analyzes narratives** — identifies ego stories and exposes their illogic
- **Returns structured responses** with identified narratives, facts, and closing questions
- **Bilingual support** — English and Hindi

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML/CSS/Vanilla JS (Netlify) |
| Backend | FastAPI + Python (Render) |
| Vector DB | Pinecone (1024-dim vectors) |
| Embeddings | multilingual-e5-large (Pinecone Inference API) |
| LLM | Groq (llama-3.3-70b-versatile) |
| RAG Framework | LangChain + Pinecone |

---

## Architecture Flow

```
User Message
    ↓
┌─────────────────────────────────────────┐
│  FRONTEND (Netlify)                     │
│  frontend/index.html                    │
└──────────────┬──────────────────────────┘
               │ HTTPS POST
               ▼
┌─────────────────────────────────────────┐
│  BACKEND (Render - FastAPI)             │
│  backend/app.py                         │
│                                         │
│  1. Receive user message                │
│  2. RAG: Embed query → Search Pinecone  │
│  3. Retrieve top-4 relevant passages    │
│  4. Build system prompt + inject context│
│  5. Call Groq LLM                       │
│  6. Parse JSON response                 │
│  7. Return with analysis                │
└──────────────┬──────────────────────────┘
               │ API Response
               ▼
┌─────────────────────────────────────────┐
│  PINECONE (Vector Database)             │
│  • 1024-dim embeddings                  │
│  • 475 chunks from PDF                  │
│  • Semantic search on every query       │
└─────────────────────────────────────────┘
```

---

## RAG Implementation

**How RAG retrieves teachings:**

1. **Document Loading** (`rag_pipeline/upload_to_pinecone.py`)
   - Load PDF using LangChain's PyPDFLoader
   - Split into 475 chunks (1000 chars, 200 char overlap)
   
2. **Embedding Generation**
   - Generate 1024-dim embeddings via Pinecone Inference API
   - Model: `multilingual-e5-large`
   - No local torch needed (saves 2GB memory)
   
3. **Vector Storage**
   - Upsert vectors to Pinecone with metadata (original text)
   - Index: 1024 dimensions, cosine similarity

4. **Query-Time Retrieval** (`backend/app.py` → `_retrieve_context()`)
   - Embed user input via Pinecone Inference API
   - Semantic search: find top-4 similar passages
   - Return passages as context for LLM

---

## LLM Implementation

**How LLM generates Acharya Prashant responses:**

1. **System Prompt** (550+ lines in `build_system_prompt()`)
   - Character voice definition: uncompromising, psychologically acute
   - Banned phrases: no wellness clichés, no generic spirituality
   - Speaking style: sharp declarations, rhetorical questions
   - Conversational examples showing exact cadence

2. **Context Injection**
   - RAG context injected into system prompt:
     ```
     ## CORE PRINCIPLES FROM ACHARYA PRASHANT'S TEACHINGS:
     [Retrieved passages from PDF]
     ```
   - Forces LLM to ground responses in actual teachings

3. **Message Flow**
   - System prompt + conversation history + user input
   - Groq API: `llama-3.3-70b-versatile` (temperature=0.45)
   - Response format: JSON (narratives, facts, questions)

4. **Output Structure**
   ```json
   {
     "narratives_identified": ["ego story 1", "ego story 2"],
     "facts_extracted": ["bare fact 1", "bare fact 2"],
     "current_narrative_being_shredded": "main illusion",
     "next_question": "sharp closing question?",
     "conversational_response": "full response in AP's voice"
   }
   ```

---

