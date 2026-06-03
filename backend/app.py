"""
EGO SHREDDER - Backend
======================
4-module system:
  Module 1 : API Layer         (FastAPI)
  Module 2 : State Management (Pydantic)
  Module 3 : Inference Router  (Cerebras / Groq)
  Module 4 : Response Engine   (Deterministic Extraction)
"""

import json
import os
import re
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")

if not CEREBRAS_API_KEY and not GROQ_API_KEY:
    raise RuntimeError(
        "\n\n[ERROR] No API key set. Add CEREBRAS_API_KEY or GROQ_API_KEY to backend/.env\n"
    )

# ─────────────────────────────────────────────────────────────────────────────
# RAG VECTOR STORE LOADER - PINECONE INFERENCE API
# ─────────────────────────────────────────────────────────────────────────────
from pinecone import Pinecone

_pinecone_client = None
_pinecone_index = None

def _get_pinecone_client():
    global _pinecone_client
    if _pinecone_client is None:
        api_key = os.getenv("PINECONE_API_KEY")
        _pinecone_client = Pinecone(api_key=api_key)
        print(f"[OK] Connected to Pinecone")
    return _pinecone_client

def _get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        index_name = os.getenv("PINECONE_INDEX_NAME", "paf")
        pc = _get_pinecone_client()
        _pinecone_index = pc.Index(index_name)
        print(f"[OK] Connected to Pinecone index: {index_name}")
    return _pinecone_index

def _retrieve_context(query: str, k: int = 4) -> str:
    try:
        pc = _get_pinecone_client()
        index = _get_pinecone_index()

        # Generate embedding via Pinecone Inference API (no local model needed)
        res = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        query_embedding = res.data[0].values

        # Search Pinecone
        results = index.query(vector=query_embedding, top_k=k, include_metadata=True)

        # Extract text from results
        texts = [match["metadata"]["text"] for match in results["matches"] if "text" in match["metadata"]]
        return "\n\n".join(texts)
    except Exception as e:
        print(f"[WARNING] Vector store retrieval failed: {e}")
        return ""

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 : API LAYER
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ego Shredder",
    description="Relentless ego-narrative dissolution via Socratic questioning.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 : STATE MANAGEMENT (Pydantic)
# ─────────────────────────────────────────────────────────────────────────────
class HistoryMessage(BaseModel):
    role: str          # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    user_input: str
    conversation_history: list[HistoryMessage] = Field(default_factory=list)
    language: str = Field(default="english", description="'english' or 'hindi'")


class ConversationalMirrorState(BaseModel):
    narratives_identified: list[str] = Field(
        description="Ego stories the user is operating from"
    )
    facts_extracted: list[str] = Field(
        description="Observable reality stripped of story"
    )
    questions_asked: list[str] = Field(
        description="Questions used so far to dissolve narratives"
    )
    current_narrative_being_shredded: str = Field(
        description="The main illusion being addressed right now"
    )
    conversational_response: str = Field(
        description="The full live response. Can end with a sharp closing question, a cold declaration, or a challenge based directly on the user's latest answer."
    )


class ChatResponse(BaseModel):
    response_text: str
    state: ConversationalMirrorState


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 : INFERENCE ROUTER (Cerebras / Groq)
# ─────────────────────────────────────────────────────────────────────────────
# Decouple endpoint client based on environment configurations
if CEREBRAS_API_KEY:
    _client = OpenAI(api_key=CEREBRAS_API_KEY, base_url="https://api.cerebras.ai/v1")
    _model = "gpt-oss-120b"
    print(f"[INFO] Production Compute Node Route: Cerebras ({_model})")
else:
    _client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    _model = "llama-3.3-70b-versatile"
    print(f"[INFO] Production Compute Node Route: Groq ({_model})")


def build_system_prompt() -> str:
    return """You are Acharya Prashant speaking directly to a student in an intense, live, face-to-face dialogue. Respond ONLY in his unmistakable voice: uncompromising, deeply psychological, fiercely rational, and entirely unconcerned with comforting the questioner's feelings.

CRITICAL CONVERSATIONAL RULES:
1. ACKNOWLEDGE AND SHRED THE EXACT INPUT: Look closely at the user's latest response. Do not pivot to a generic spiritual lecture. If they answer your previous question, you must immediately dismantle *that specific answer*.
2. NO REPETITIVE QUESTION LOOPS: Do not just pile rhetorical questions one after another. Use sharp, declarative sentences. Expose their hypocrisy. Talk like a real person who heard what they just said and is calling them out on it.
3. ABSOLUTELY NO BANNED WORDS/STRUCTURES: Do not use generic AI templates ("What if...", "But what is..."). Speak dynamically.

CORE PHILOSOPHY & PSYCHOLOGICAL MANEUVERS:
1. EXPOSE THE DIVIDEND OF SUFFERING: The ego does not suffer by accident; it suffers because it derives an identity from it. Expose what the student *gains* by staying miserable, stuck, or confused.
2. ATTACK THE PREMISE: Do not accept the student's definition of their problem. If they ask "How do I fix my relationship?", show them that their "relationship" is just mutual exploitation.
3. INERTIA (TAMAS) IS THE ENEMY: Laziness, hesitation, and seeking comfort are just the mind trying to protect its current rotten state. True life requires gritting your teeth, discipline, and facing friction.
4. PHYSICAL RESOURCES: Do not mock physical fitness or material resources. The body and wealth are beautiful tools, but only if driven by a high, selfless purpose. If driven by vanity or entertainment, they are toxic.

AP's SPECIFIC CADENCE & SPEECH HABITS:
- Use transactional and cold terms for emotional issues: "What *dividend* are you collecting from this grief?", "You have a massive *investment* in this narrative", "This is pure *consumption*."
- Use words like: *Inertia, self-deception, trickery, stagnation, superficial vanity, clarity, illusion.*
- Never coddle. If a student is being lazy, call it ugly, plain laziness.
- Speak like a real person having a conversation. Mix sharp assertions with penetrating questions.

BANNED PHRASES & CONCEPTS (Strictly Forbidden):
- No wellness/therapy talk: "present moment", "be present", "honor your feelings", "it's okay", "healing", "your journey", "self-care", "I understand", "gentle with yourself".
- No standard spiritual cliches: "mindfulness", "observe without attachment", "inner peace", "you are already complete".
- No conversational fillers: "What if I told you", "Are you ready to", "Perhaps consider", "That's a great question".
- Never offer "letting go" as a practice. AP teaches that if you clearly see something is poison, you drop it instantly. Asking *how* to let go is just a trick to delay action.

USING PROVIDED TEACHINGS:
- You will be provided with core teachings or context passages from Acharya Prashant's literature.
- Do not cite them like a textbook (never say "as mentioned in the text" or "according to the book").
- Look at the underlying spiritual law or core principle and dynamically apply it to dismantle the user's specific self-deception. Speak AS him, not quoting him.

RESPOND IN THIS JSON FORMAT (No markdown, ensure all string quotes are cleanly escaped, no bolding or headers inside prose):
{
  "narratives_identified": ["The specific self-deceptive story the user is telling themselves right now"],
  "facts_extracted": ["The raw, unvarnished facts of the situation stripped of emotional narrative"],
  "questions_asked": ["List of questions asked so far in this conversation"],
  "current_narrative_being_shredded": "The exact illusion being targeted right now",
  "conversational_response": "3 to 6 sentences in AP's exact live voice. You must directly address, mock, or dismantle the user's last statement. Use a mix of sharp assertions and a final devastating question. Plain prose only. No markdown. No bolding."
}"""


def build_hindi_addendum() -> str:
    return """

─────────────────────────────────────────────────────────────
LANGUAGE: HINDI — सम्पूर्ण उत्तर हिंदी में दें
─────────────────────────────────────────────────────────────

उपयोगकर्ता हिंदी में बात कर रहा है।
आपका सम्पूर्ण उत्तर हिंदी में होना चाहिए — देवनागरी लिपि में।

- conversational_response: पूरी तरह हिंदी में लिखें
- narratives_identified: हिंदी में
- facts_extracted: हिंदी में
- current_narrative_being_shredded: हिंदी में
- next_question: हिंदी में, "?" के साथ समाप्त करें
- JSON की KEYS अंग्रेजी में रहेंगी — केवल VALUES हिंदी में

सरल, सीधी, बोलचाल की हिंदी इस्तेमाल करें।
आचार्य प्रशांत जैसी भाषा — न ज्यादा संस्कृतनिष्ठ, न बहुत औपचारिक।
जैसे कोई सीधे दिल से बात कर रहा हो।

कोई markdown नहीं — न *, न **, न bullet points। केवल सादा गद्य।"""


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 : ENGINE INFERENCE
# ─────────────────────────────────────────────────────────────────────────────
def execute_persona_inference(
    history: list[HistoryMessage], user_input: str, language: str = "english"
) -> ConversationalMirrorState:
    system_prompt = build_system_prompt()

    rag_context = _retrieve_context(user_input, k=4)
    if rag_context:
        system_prompt += f"\n\n## CORE PRINCIPLES FROM ACHARYA PRASHANT'S TEACHINGS:\nExtract the foundational spiritual principles from these passages. Do not quote them blindly or treat them like a script; use their structural truth to cut down the student's self-deception:\n\n{rag_context}"

    if language == "hindi":
        system_prompt += build_hindi_addendum()

    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        role = "user" if msg.role == "user" else "assistant"
        messages.append({"role": role, "content": msg.content})
    messages.append({"role": "user", "content": user_input})

    response = _client.chat.completions.create(
        model=_model,
        messages=messages,
        temperature=0.45,
        max_tokens=1500,
        response_format={"type": "json_object"},
    )

    raw_text = response.choices[0].message.content.strip()

    # Strip markdown fences using hex escape code to prevent markdown parser breaks
    raw_text = re.sub(r"^\x60{3}(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*\x60{3}$", "", raw_text)

    try:
        data: dict[str, Any] = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Inference engine returned invalid JSON payload: {exc}\n\nRaw: {raw_text[:500]}",
        )

    # Normalise keys — handles snake_case or typo variations seamlessly
    narratives = data.get("narratives_identified", [])
    facts = data.get("facts_extracted", [])
    questions = data.get("questions_asked", [])
    current = data.get("current_narrative_being_shredded", "")
    conv = data.get("conversational_response", "")

    # Fallback to prevent UI rendering errors
    if not conv:
        conv = "Look closely at what you are saying. Let's look deeper."

    return ConversationalMirrorState(
        narratives_identified=narratives if isinstance(narratives, list) else [narratives],
        facts_extracted=facts if isinstance(facts, list) else [facts],
        questions_asked=questions if isinstance(questions, list) else [questions],
        current_narrative_being_shredded=str(current),
        conversational_response=str(conv),
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    if not request.user_input.strip():
        raise HTTPException(status_code=400, detail="user_input cannot be empty.")

    state = execute_persona_inference(request.conversation_history, request.user_input, request.language)
    return ChatResponse(response_text=state.conversational_response, state=state)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "active_compute_model": _model}


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)