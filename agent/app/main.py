import os
import json
import redis
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicjalizacja Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Model danych

class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None


class FileUploadRequest(BaseModel):
    file_type: str
    content: str


class ContextRequest(BaseModel):
    context_key: str
    context_data: str


class SettingsRequest(BaseModel):
    scale: float

# Inicjalizacja aplikacji FastAPI
app = FastAPI(title="GoodFix AI Agent", version="1.0.0")

# Funkcje pomocnicze

def get_context(key: str) -> Optional[str]:
    """Pobiera kontekst z Redis"""
    try:
        return redis_client.get(key)
    except Exception as e:
        logger.error(f"Błąd podczas pobierania kontekstu: {e}")
        return None


def set_context(key: str, value: str) -> bool:
    """Ustawia kontekst w Redis"""
    try:
        redis_client.setex(key, 3600, value)  # Czas ważności 1 godzina
        return True
    except Exception as e:
        logger.error(f"Błąd podczas ustawiania kontekstu: {e}")
        return False


def search_electronics_schematic(query: str) -> str:
    """Wyszukuje schemat elektroniczny w internecie"""
    try:
        # W tym miejscu można dodać integrację z API wyszukiwania
        # Na potrzeby prototypu zwracamy przykładowy wynik
        return f"Wyniki wyszukiwania dla: {query}"
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania schematu: {e}")
        return "Błąd podczas wyszukiwania schematu elektronicznego"


def process_file_upload(file_type: str, content: str) -> str:
    """Przetwarza przesłany plik"""
    try:
        # Zapisz plik do katalogu
        os.makedirs("uploaded_files", exist_ok=True)
        filename = f"uploaded_files/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_type}.txt"
        with open(filename, "w") as f:
            f.write(content)
        return f"Plik zapisany: {filename}"
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania pliku: {e}")
        return "Błąd podczas przetwarzania pliku"


def generate_context_summary() -> str:
    """Generuje podsumowanie kontekstu pracy"""
    try:
        keys = redis_client.keys("context:*")
        summary = "Podsumowanie kontekstu:\n"
        for key in keys:
            value = redis_client.get(key)
            if value:
                summary += f"- {key}: {value[:100]}...\n"
        return summary
    except Exception as e:
        logger.error(f"Błąd podczas generowania podsumowania: {e}")
        return "Błąd podczas generowania podsumowania kontekstu"

# Endpointy API

@ app.post("/chat")
async def chat(request: ChatRequest):
    """Endpoint do komunikacji z agentem"""
    try:
        # Sprawdź kontekst
        if request.context:
            set_context("current_context", request.context)
        
        # Sprawdź czy to zapytanie o schemat
        if "schemat" in request.message.lower() or "elektronika" in request.message.lower():
            query = request.message.replace("schemat", "").replace("elektronika", "").strip()
            result = search_electronics_schematic(query)
            return {"response": result}
        
        # Sprawdź czy to zapytanie o podsumowanie
        if "podsumowanie" in request.message.lower():
            summary = generate_context_summary()
            return {"response": summary}
        
        # Domyślne zachowanie - odpowiedź na zapytanie
        return {"response": "To jest odpowiedź agenta. Proszę o więcej szczegółów, jeśli chcesz, bym pomógł w konkretnym aspekcie."}
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania zapytania: {e}")
        raise HTTPException(status_code=500, detail="Błąd serwera")


@ app.post("/upload_file")
async def upload_file(request: FileUploadRequest):
    """Endpoint do przesyłania plików"""
    try:
        result = process_file_upload(request.file_type, request.content)
        return {"message": result}
    except Exception as e:
        logger.error(f"Błąd podczas przesyłania pliku: {e}")
        raise HTTPException(status_code=500, detail="Błąd serwera")


@ app.post("/set_context")
async def set_context_endpoint(request: ContextRequest):
    """Endpoint do ustawiania kontekstu"""
    try:
        success = set_context(request.context_key, request.context_data)
        if success:
            return {"message": "Kontekst ustawiony pomyślnie"}
        else:
            raise HTTPException(status_code=500, detail="Błąd podczas ustawiania kontekstu")
    except Exception as e:
        logger.error(f"Błąd podczas ustawiania kontekstu: {e}")
        raise HTTPException(status_code=500, detail="Błąd serwera")


@ app.get("/get_context/{key}")
async def get_context_endpoint(key: str):
    """Endpoint do pobierania kontekstu"""
    try:
        context = get_context(key)
        if context:
            return {"context": context}
        else:
            raise HTTPException(status_code=404, detail="Kontekst nie znaleziony")
    except Exception as e:
        logger.error(f"Błąd podczas pobierania kontekstu: {e}")
        raise HTTPException(status_code=500, detail="Błąd serwera")


@ app.post("/settings")
async def update_settings(request: SettingsRequest):
    """Endpoint do aktualizacji ustawień"""
    try:
        # Zapisz ustawienia w Redis
        set_context("settings:scale", str(request.scale))
        return {"message": f"Ustawienia zaktualizowane: skala {request.scale}%"}
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji ustawień: {e}")
        raise HTTPException(status_code=500, detail="Błąd serwera")


@ app.get("/health")
async def health_check():
    """Endpoint do sprawdzenia stanu serwera"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)