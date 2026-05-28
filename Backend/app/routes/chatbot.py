"""Chatbot route: single endpoint for AI chat."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import chat_service, schemas
from ..core.database import get_db

router = APIRouter(tags=["chatbot"])


@router.post("/api/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    return chat_service.process_chat_request(payload, db)
