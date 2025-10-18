"""
FastAPI Backend for Suyash - Generative AI Chatbot
Main entry point for the API
"""
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.pipelines.chat_orchestrator import ChatOrchestrator
from app.models import ChatMessage, AgentResponse
from app.config import settings
from app.services.qdrant_service import qdrant_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Suyash - Generative AI Chatbot API",
    description="Multi-agent chatbot specializing in Generative AI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of orchestrator
_orchestrator = None

def get_orchestrator() -> ChatOrchestrator:
    """Get or create the chat orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        logger.info("Initializing ChatOrchestrator...")
        _orchestrator = ChatOrchestrator()
    return _orchestrator

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str
    session_id: str
    confidence: float
    sources: List[dict]
    metadata: dict
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    details: Optional[dict] = None

class ConversationHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    message_count: int


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc)
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc)
    )

@app.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check that also reports Qdrant connectivity state."""
    # Attempt a lightweight ensure; do not raise
    connected = qdrant_service._ensure_client()
    details = {
        "qdrant_connected": bool(qdrant_service.client is not None),
        "qdrant_url": settings.qdrant_url,
    }
    return HealthResponse(
        status="ready" if connected and qdrant_service.client is not None else "degraded",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
        details=details,
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user messages through the multi-agent system
    
    Args:
        request: ChatRequest with message and optional session_id
        
    Returns:
    ChatResponse with Suyash's response and metadata
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Received chat request for session {session_id}")
        
        # Create ChatMessage
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Process through orchestrator
        orchestrator = get_orchestrator()
        response = await orchestrator.process_message(
            message=user_message,
            session_id=session_id
        )
        
        # Format sources for response
        sources_formatted = [
            {
                "title": source.get("title", "Unknown"),
                "url": source.get("url", ""),
                "type": source.get("type", "unknown"),
                "relevance": source.get("relevance", 0.0)
            }
            for source in response.sources
        ]
        
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            confidence=response.confidence,
            sources=sources_formatted,
            metadata=response.metadata,
            timestamp=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

@app.get("/conversation/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_id: str):
    """
    Retrieve conversation history for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        ConversationHistoryResponse with message history
    """
    try:
        orchestrator = get_orchestrator()
        messages = await orchestrator.get_conversation_history(session_id)
        
        messages_formatted = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=messages_formatted,
            message_count=len(messages_formatted)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    try:
        orchestrator = get_orchestrator()
        success = await orchestrator.clear_conversation(session_id)
        
        if success:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": f"Conversation {session_id} cleared successfully"}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {session_id} not found"
            )
            
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation: {str(e)}"
        )

@app.get("/persona")
async def get_persona():
    """
    Get Suyash's persona information
    
    Returns:
        Persona details
    """
    return JSONResponse(
        content={
            "name": settings.persona_name,
            "role": "Research Analyst specializing in Generative AI",
            "background": "Engineer and AI enthusiast focused on ML and NLP",
            "interests": ["AI libraries", "emerging GenAI models", "research papers", "industry trends"],
            "style": "Friendly, curious, and thoughtful"
        }
    )


if __name__ == "__main__":
    import uvicorn
    import sys

    logger.info("Starting Suyash chatbot API server...")
    try:
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level="info",
        )
    except KeyboardInterrupt:
        # Graceful shutdown without noisy traceback
        logger.info("Server shutdown requested (KeyboardInterrupt). Exiting cleanly...")
        sys.exit(0)
    except Exception as e:
        logger.exception("Server terminated due to unexpected error: %s", e)
        raise
