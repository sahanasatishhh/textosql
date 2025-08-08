
# api/main.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from langchain_utils import invoke_chain   # ← your existing function

load_dotenv()
app = FastAPI(title="NL2SQL Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_DIR = Path(__file__).parent / "transcripts"
LOG_DIR.mkdir(exist_ok=True)

class ChatRequest(BaseModel):
    question: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str

def log_to_txt(session_id:str,question: str, answer: str):
    """
    Append the Q/A pair to today's transcript file.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # one file per day; change to chat-uuid if you prefer per-session
    log_file = LOG_DIR / f"{ts/session_id}.txt"   
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] USER: {question}\n")
        f.write(f"[{ts}] BOT : {answer}\n\n")


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        answer = invoke_chain(req.question)
        
        log_to_txt(req.session_id,req.question, answer)

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Optional tiny health-check
@app.get("/health")
async def health():
    return {"status": "ok"}
