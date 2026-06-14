# Ego Shredder

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
| Frontend | React + Vite (Netlify) |
| Backend | FastAPI + Python (Render) |
| Vector DB | Pinecone (1024-dim vectors) |
| Embeddings | multilingual-e5-large (Pinecone Inference API) |
| LLM | Cerebras / Groq (llama-3.3-70b-versatile fallback) |

---

<!--## Project Structure

```
Ego Shredder/
├── frontend-react/          # React frontend (deployed on Netlify)
│   ├── src/
│   │   ├── App.jsx          # Main app — state, send() logic
│   │   ├── strings.js       # All UI language strings (EN + HI)
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── ChatWindow.jsx
│   │       ├── MessageBubble.jsx
│   │       ├── InputBar.jsx
│   │       └── ThinkingDots.jsx
│   └── index.html
├── backend/
│   └── app.py               # FastAPI backend (deployed on Render)
└── rag_pipeline/            # One-time setup scripts (already run)
    ├── upload_to_pinecone.py
    └── AcharyaPrashantBook.pdf
```

--->

<!--## Architecture Flow

```
User Message
    ↓
┌─────────────────────────────────────────┐
│  FRONTEND (Netlify)                     │
│  React + Vite (frontend-react/)         │
└──────────────┬──────────────────────────┘
               │ HTTPS POST /api/chat
               ▼
┌─────────────────────────────────────────┐
│  BACKEND (Render - FastAPI)             │
│  backend/app.py                         │
│                                         │
│  1. Receive user message                │
│  2. RAG: Embed query → Search Pinecone  │
│  3. Retrieve top-4 relevant passages    │
│  4. Build system prompt + inject context│
│  5. Call LLM (Cerebras / Groq)         │
│  6. Parse JSON response                 │
│  7. Return structured state             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  PINECONE (Vector Database)             │
│  • 1024-dim embeddings                  │
│  • ~475 chunks from PDF                 │
│  • Semantic search on every query       │
└─────────────────────────────────────────┘
```

--->

## Video-DEMO
<video src="https://github.com/user-attachments/assets/78980a93-565f-4549-b6bb-ca8ffb291b96" controls width="100%"></video>



---

## Local Development

**Frontend:**
```bash
cd frontend-react
npm install
npm run dev
# Opens on http://localhost:5173
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

---


