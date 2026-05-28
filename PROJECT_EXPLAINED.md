# Ego Shredder — Full Project Breakdown

## What the app does

User types a personal problem → Frontend sends it to Backend → Backend sends it to Google's Gemini AI with a carefully crafted instruction → Gemini returns a structured response → Frontend displays it beautifully.

---

# BACKEND

**File:** `backend/app.py`  
**Language:** Python

---

## 1. FastAPI — The Web Framework

```python
from fastapi import FastAPI
app = FastAPI()
```

**What it is:** FastAPI is a modern Python web framework for building APIs.

**What an API is:** An API (Application Programming Interface) is just a way for two programs to talk to each other. Your frontend (browser) talks to your backend (Python) through an API.

**Why FastAPI specifically:**
- Extremely fast
- Automatically validates incoming data
- Auto-generates docs at `http://127.0.0.1:8000/docs` — you can test your API there

---

## 2. Uvicorn — The Server

```python
uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
```

**What it is:** Uvicorn is the actual server that listens for requests on port 8000.

**Analogy:** FastAPI is the restaurant, Uvicorn is the building it runs inside. Without Uvicorn, FastAPI has no place to live.

**`reload=True`** means the server automatically restarts when you change the code — useful during development.

---

## 3. CORS Middleware

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

**What it is:** CORS (Cross-Origin Resource Sharing) is a browser security rule.

**The problem it solves:** By default, browsers block requests from one domain to another. Your frontend runs on `file://` or `netlify.com`, and your backend runs on `localhost:8000` or `render.com` — these are different origins, so the browser would block it.

**`allow_origins=["*"]`** tells the browser: "This API is open to everyone." The `*` means any origin is allowed.

---

## 4. python-dotenv — Environment Variables

```python
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
```

**What it is:** Reads your `.env` file and loads the values as environment variables.

**Why not hardcode the key?** If you hardcode `GOOGLE_API_KEY = "AIza..."` in your Python file and push to GitHub, everyone can see and steal your key. The `.env` file stays on your machine only (because it's in `.gitignore`).

---

## 5. Pydantic — Data Validation (Module 2)

```python
class ChatRequest(BaseModel):
    user_input: str
    conversation_history: list[HistoryMessage]
    language: str = "english"
```

**What it is:** Pydantic automatically validates the data coming into your API.

**Why it matters:** When the frontend sends a request, Pydantic checks:
- Is `user_input` a string? ✓
- Is `conversation_history` a list? ✓
- If something is wrong, it automatically sends back a `422 error` with a clear message

Without Pydantic, you'd have to manually check every field yourself.

```python
class ConversationalMirrorState(BaseModel):
    narratives_identified: list[str]
    facts_extracted: list[str]
    questions_asked: list[str]
    current_narrative_being_shredded: str
    next_question: str
    conversational_response: str
```

This defines exactly what shape Gemini's response must take — it's the contract between your app and the AI.

---

## 6. Google Gemini — The AI (Module 3)

```python
from google import genai
_gemini_client = genai.Client(api_key=GOOGLE_API_KEY)
```

**What it is:** Gemini is Google's large language model (like ChatGPT but by Google). You're using the `gemini-2.5-flash` model — fast and capable.

**How you're calling it:**

```python
response = _gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=contents,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.35,
        response_mime_type="application/json",
    ),
)
```

**Key parameters explained:**

| Parameter | What it does |
|-----------|-------------|
| `system_instruction` | The big prompt that tells Gemini to behave like Acharya Prashant |
| `temperature=0.35` | Low = more focused/consistent, High = more creative/random (0 to 1) |
| `top_p=0.9` | Controls diversity of word choices |
| `max_output_tokens=1500` | Limits response length |
| `response_mime_type="application/json"` | Forces Gemini to reply in JSON format |

---

## 7. The System Prompt — Prompt Engineering

```python
def build_system_prompt() -> str:
    return """You are speaking as Acharya Prashant speaks..."""
```

**What it is:** The system prompt is the set of instructions you give the AI before the conversation starts. The user never sees it.

**This is called Prompt Engineering** — the art of writing instructions that make the AI behave exactly how you want.

Your prompt is very detailed — it defines:
- The teaching philosophy (Ego vs Mind vs Witness)
- Specific response patterns (LEVEL 1, LEVEL 2, LEVEL 3)
- The exact JSON format the AI must return
- Rules like "NO MARKDOWN EVER"

The better your system prompt, the better your AI behaves.

---

## 8. Conversation History

```python
def _build_contents(history: list[HistoryMessage], user_input: str):
    contents = []
    for msg in history:
        role = "user" if msg.role == "user" else "model"
        contents.append(Content(role=role, parts=[Part(text=msg.content)]))
    contents.append(Content(role="user", parts=[Part(text=user_input)]))
    return contents
```

**The problem:** AI models have no memory. Every API call starts fresh.

**The solution:** Every time the user sends a message, the frontend sends the **entire conversation history** along with it. The backend reconstructs the full conversation and passes it to Gemini, so Gemini has context of everything said before.

This is how every chatbot works — memory is an illusion created by replaying history.

---

## 9. The API Endpoint

```python
@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    state = call_gemini(request.conversation_history, request.user_input, request.language)
    return ChatResponse(response_text=state.conversational_response, state=state)
```

**`@app.post("/api/chat")`** means: when someone sends a POST request to `/api/chat`, run this function.

**`async`** means this function is non-blocking — while waiting for Gemini to respond, the server can handle other requests. Essential for performance.

---
---

# FRONTEND

**File:** `frontend/index.html`  
**Languages:** HTML, CSS, JavaScript (all in one file)

---

## 1. HTML Structure

The page has 4 main parts:

```
<header>              → Top bar with title + language toggle
<div id="chat">       → Scrollable message area
<div class="input-area"> → Textarea + Send button
<div id="error-toast">   → Error popup
```

This is a **Single Page Application (SPA)** — everything happens on one page without reloading.

---

## 2. CSS Variables — The Design System

```css
:root {
  --bg:      #f6f3ee;
  --accent:  #a83222;
  --text:    #1c1814;
  ...
}
```

**What CSS variables are:** Instead of repeating `#a83222` everywhere, you define it once as `--accent` and use it everywhere. If you want to change the red color, you change it in one place.

**`:root`** means these variables are available globally across all CSS.

---

## 3. Flexbox Layout

```css
body {
  display: flex;
  flex-direction: column;
  height: 100dvh;
}
#chat { flex: 1; overflow-y: auto; }
```

**What Flexbox is:** A CSS layout system that makes it easy to arrange elements in rows or columns.

**`flex: 1`** on the chat area means: "take up all remaining space after the header and input bar have their space." This is how the chat area fills the whole screen without overflow.

**`100dvh`** = 100% of the device viewport height — works correctly on mobile browsers too.

---

## 4. The Fetch API — Talking to the Backend

```javascript
const res = await fetch(`${BACKEND}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        user_input: text,
        conversation_history: history,
        language: language,
    }),
});
```

**What Fetch is:** The browser's built-in way to make HTTP requests to a server. This is how the frontend calls your Python backend.

**`JSON.stringify`** converts a JavaScript object into a JSON string for sending.

**`await`** pauses execution until the server responds — without it, the code would move on before the response arrives.

---

## 5. Conversation History in the Frontend

```javascript
let history = [];

// After each exchange:
history.push({ role: "user",      content: text });
history.push({ role: "assistant", content: data.response_text });
```

The frontend keeps a growing array of all messages. Every time the user sends a message, this full array is sent to the backend, which passes it to Gemini — this is the memory system explained earlier.

---

## 6. XSS Protection

```javascript
function escHtml(s) {
    return String(s)
      .replace(/&/g,"&amp;").replace(/</g,"&lt;")
      .replace(/>/g,"&gt;")...
}
```

**What XSS is:** Cross-Site Scripting. If a user types `<script>alert('hacked')</script>` and you display it raw in HTML, the browser would execute it as code.

**What `escHtml` does:** Converts dangerous characters like `<` into `&lt;` so the browser displays them as text, not code. Always do this when showing user input on screen.

---

## 7. Language Toggle

```javascript
let language = "english";

function toggleLang() {
    language = language === "english" ? "hindi" : "english";
    // update UI strings...
}
```

The `UI` object holds all text in both languages. When toggled, the UI updates immediately. The `language` variable is sent to the backend with every request, and the backend adds a Hindi addendum to the system prompt if needed.

---

## 8. Auto-growing Textarea

```javascript
inputEl.addEventListener("input", () => {
    inputEl.style.height = "auto";
    inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
});
```

Every time the user types, the textarea's height is reset to `auto` then set to its scroll height — making it grow with the content up to a max of 160px.

---

## 9. Thinking Animation

```javascript
function appendThinking() {
    el.innerHTML = "<span></span><span></span><span></span>";
    chatEl.appendChild(el);
}
function removeThinking() { el.remove(); }
```

Three dots appear while waiting for the backend. They're CSS-animated with staggered delays to create a pulsing effect. Removed as soon as the response arrives.

---

# Full Request Flow (End to End)

```
User types message → presses Enter
        ↓
Frontend appends user bubble to chat
Frontend shows thinking dots
Frontend sends POST to /api/chat with {user_input, history, language}
        ↓
Backend receives request → Pydantic validates it
Backend rebuilds full conversation history
Backend calls Gemini API with system prompt + history
        ↓
Gemini thinks → returns JSON response
        ↓
Backend parses JSON → validates with Pydantic
Backend returns ChatResponse to frontend
        ↓
Frontend removes thinking dots
Frontend renders the response (body + highlighted question)
Frontend appends both messages to history array
```

---

# Tech Stack Summary

| Tool | Layer | Purpose |
|------|-------|---------|
| HTML/CSS/JS | Frontend | UI, layout, interaction |
| Fetch API | Frontend | HTTP calls to backend |
| FastAPI | Backend | Web framework, routing |
| Uvicorn | Backend | ASGI server |
| Pydantic | Backend | Data validation |
| python-dotenv | Backend | Secure API key loading |
| Google Gemini | External | The AI brain |
| Prompt Engineering | Backend | Controls AI behavior |
