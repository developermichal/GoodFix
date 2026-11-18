import os
import sys
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from dotenv import load_dotenv

# Wczytanie zmiennych środowiskowych
load_dotenv()

# Importy lokalne
from .email_handler import EmailHandler
from .session_manager import SessionManager
from .redis_context_manager import RedisContextManager

# Inicjalizacja komponentów
app = FastAPI(title="GoodFix AI Agent")
email_handler = EmailHandler()
session_manager = SessionManager()
redis_manager = RedisContextManager()

# Modele danych

class SessionCreate(BaseModel):
    session_id: str
    context: Dict[str, Any]

# Endpointy

@ app.get("/health")
def health_check():
    return {"status": "healthy"}

@ app.post("/sessions")
def create_session(session_data: SessionCreate):
    try:
        session_id = session_manager.create_session(session_data.session_id, session_data.context)
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ app.get("/sessions/{session_id}")
def get_session(session_id: str):
    try:
        session = session_manager.get_session(session_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ app.get("/emails")
def get_emails():
    try:
        emails = email_handler.fetch_emails()
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ app.post("/emails/send")
def send_email(to: str, subject: str, body: str):
    try:
        email_handler.send_email(to, subject, body)
        return {"status": "email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpointy dla kontekstu

@ app.get("/context")
def get_context():
    try:
        context = redis_manager.get_global_context()
        return {"context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ app.post("/context")
def set_context(context_data: Dict[str, Any]):
    try:
        redis_manager.set_global_context(context_data)
        return {"status": "context updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpointy dla sesji

@ app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    try:
        session_manager.delete_session(session_id)
        return {"status": "session deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@ app.put("/sessions/{session_id}")
def update_session(session_id: str, session_data: Dict[str, Any]):
    try:
        session_manager.update_session(session_id, session_data)
        return {"status": "session updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpointy dla testów

@ app.get("/test")
def test_endpoint():
    return {"message": "Test endpoint works"}

# Obsługa błędów

@ app.exception_handler(Exception)
def global_exception_handler(request, exc):
    logging.error(f"Global exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)