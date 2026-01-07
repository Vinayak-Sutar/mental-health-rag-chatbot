"""
FastAPI Backend for Mental Health Chatbot
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.pipeline import RAGPipeline
from src.safety import get_safety_layer

app = FastAPI(title="Mental Health Support API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store sessions in memory (use Redis/DB for production)
sessions: dict = {}


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str
    is_crisis: bool


class Session(BaseModel):
    id: str
    messages: List[Message]
    created_at: str


def get_or_create_session(session_id: Optional[str]) -> tuple:
    """Get existing session or create new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    new_id = str(uuid.uuid4())[:8]
    sessions[new_id] = {
        "pipeline": RAGPipeline(),
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    return new_id, sessions[new_id]


@app.get("/")
def root():
    return {"message": "Mental Health Support API", "status": "running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message and get a response."""
    session_id, session = get_or_create_session(request.session_id)
    
    # Add user message
    session["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get response from pipeline
    try:
        result = session["pipeline"].process(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Add assistant message
    session["messages"].append({
        "role": "assistant",
        "content": result["response"],
        "timestamp": datetime.now().isoformat()
    })
    
    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        intent=result["intent"],
        is_crisis=result["is_crisis"]
    )


@app.get("/session/{session_id}")
def get_session(session_id: str):
    """Get session history."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "id": session_id,
        "messages": session["messages"],
        "created_at": session["created_at"]
    }


@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    """Clear a session."""
    if session_id in sessions:
        sessions[session_id]["pipeline"].reset()
        sessions[session_id]["messages"] = []
    return {"message": "Session cleared"}


@app.get("/sessions")
def list_sessions():
    """List all active sessions."""
    return [
        {"id": sid, "message_count": len(s["messages"]), "created_at": s["created_at"]}
        for sid, s in sessions.items()
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
