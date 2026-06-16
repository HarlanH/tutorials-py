"""Track 48: chat frontend over a SQL database.

FastAPI backend that accepts a chat message plus conversation history,
optionally rephrases follow-up questions, runs the SQLAgent, and returns
the answer together with the SQL that was written.
"""

from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from opensymbolicai.llm import LLMConfig, create_llm

from ollama import check_ollama
from sql_agent import SQLAgent

MODEL = "qwen2.5-coder:7b"
DB_PATH = "chinook.db"
DB_URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"

app = FastAPI()

# Initialised once at startup
_llm: object = None
_agent: SQLAgent = None
_schema: str = ""


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Message(BaseModel):
    role: str   # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []

class ChatResponse(BaseModel):
    answer: str
    sql: str
    rephrased: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_db() -> None:
    if Path(DB_PATH).exists():
        return
    print("Downloading Chinook database...")
    urllib.request.urlretrieve(DB_URL, DB_PATH)
    print(f"  Saved {DB_PATH}\n")


def rephrase(question: str, history: list[Message]) -> str | None:
    """Rewrite a follow-up question as a standalone question.

    Returns the rephrased string, or None if the question was already standalone.
    """
    if not history:
        return None
    turns = "\n".join(
        f"{m.role.capitalize()}: {m.content}" for m in history[-6:]
    )
    prompt = (
        f"Conversation so far:\n{turns}\n\n"
        f"Follow-up question: {question}\n\n"
        "Rewrite the follow-up as a complete, standalone question that can be "
        "understood without the conversation history. "
        "If it is already standalone, output it unchanged. "
        "Output only the rewritten question, nothing else."
    )
    result = _llm.generate(prompt).text.strip()
    return result if result.lower() != question.lower() else None


def extract_sql(plan: str) -> str:
    """Pull the SQL string out of the agent's plan.

    Searches for the SELECT statement directly to avoid quote-nesting issues
    when the SQL contains string literals (e.g. WHERE x IN ('a', 'b')).
    """
    match = re.search(r'(SELECT\b.+)', plan, re.DOTALL | re.IGNORECASE)
    if not match:
        return ""
    sql = match.group(1)
    # Trim at closing triple-quote, return statement, or next assignment
    for stop in ['"""', "'''", '\nreturn ', '\nresult ']:
        idx = sql.find(stop)
        if 0 < idx:
            sql = sql[:idx]
    return sql.strip().rstrip(';').strip()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    global _llm, _agent, _schema
    if not check_ollama(MODEL):
        print(f"Ollama check failed for {MODEL}. Start Ollama and pull the model.")
        sys.exit(1)
    ensure_db()
    _llm = create_llm(LLMConfig(provider="ollama", model=MODEL))
    _agent = SQLAgent(db_path=DB_PATH, llm=_llm)
    _schema = _agent.full_schema()
    print(f"Ready — model={MODEL}  db={DB_PATH}  → http://127.0.0.1:8048")


@app.get("/")
async def index() -> HTMLResponse:
    return HTMLResponse(Path("chat.html").read_text())


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    rephrased = rephrase(req.message, req.history)
    question = rephrased or req.message

    task = f"Database schema:\n{_schema}\n\nQuestion: {question}"
    result = _agent.run(task)
    answer = result.result if isinstance(result.result, str) else "(no result)"

    # Retry once if the model generated invalid SQL
    if answer.startswith("SQL error"):
        result = _agent.run(task)
        answer = result.result if isinstance(result.result, str) else "(no result)"

    sql = extract_sql(result.plan or "")
    return ChatResponse(answer=answer, sql=sql, rephrased=rephrased)
