from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Document(BaseModel):
    id: str
    text: str
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    role: str  # user|assistant|system
    content: str
    timestamp: Optional[datetime] = None

class AgentResponse(BaseModel):
    """Standardized response used across agents and orchestrator"""
    content: str
    agent: str
    confidence: float = 1.0
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class ConversationState(BaseModel):
    """State of the conversation"""
    session_id: str
    messages: List[ChatMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: List[ChatMessage] = Field(default_factory=list)

class ClarifyingQuestion(BaseModel):
    question: str

class ChatResponse(BaseModel):
    session_id: str
    clarifying_questions: List[ClarifyingQuestion] = Field(default_factory=list)
    answer: Optional[str] = None
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Optional[Dict[str, Any]] = None
    persona_intro: Optional[str] = None

class IngestItem(BaseModel):
    id: str
    text: str
    source: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IngestRequest(BaseModel):
    items: List[IngestItem]
    collection: Optional[str] = None