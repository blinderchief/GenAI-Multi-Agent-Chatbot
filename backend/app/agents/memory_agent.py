"""
Memory Agent - Manages session state and long-term user memory.
"""
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json

from app.services.qdrant_service import qdrant_service
from app.config import settings

logger = logging.getLogger(__name__)


class MemoryAgent:
    """Agent responsible for managing user memory and session state."""
    
    def __init__(self):
        """Initialize memory agent."""
        self.qdrant = qdrant_service
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=settings.session_timeout_minutes)
        logger.info("MemoryAgent initialized")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get or create a session.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            Session data.
        """
        # Check if session exists and is not expired
        if session_id in self.sessions:
            session = self.sessions[session_id]
            last_activity = session.get("last_activity")
            
            if last_activity and datetime.now() - last_activity < self.session_timeout:
                # Update last activity
                session["last_activity"] = datetime.now()
                return session
        
        # Create new session
        logger.info(f"Creating new session: {session_id}")
        session = {
            "session_id": session_id,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "conversation_history": [],
            "user_preferences": {},
            "clarified_intent": {},
            "message_count": 0
        }
        
        self.sessions[session_id] = session
        return session
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to conversation history.
        
        Args:
            session_id: Session identifier.
            role: Message role (user/assistant).
            content: Message content.
            metadata: Optional metadata.
        """
        session = self.get_session(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        session["conversation_history"].append(message)
        session["message_count"] += 1
        
        # Limit history size
        max_history = settings.max_session_history
        if len(session["conversation_history"]) > max_history:
            # Optionally summarize old messages before removing
            if settings.enable_history_summarization:
                self._summarize_old_history(session)
            else:
                # Simply truncate
                session["conversation_history"] = session["conversation_history"][-max_history:]
        
        logger.info(f"Added {role} message to session {session_id}")
    
    def get_conversation_history(
        self,
        session_id: str,
    limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history for a session.
        
        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to return.
            
        Returns:
            List of messages.
        """
        session = self.get_session(session_id)
        history = session.get("conversation_history", [])
        
        if limit:
            return history[-limit:]
        
        return history
    
    def store_long_term_memory(
        self,
        session_id: str,
        memory_text: str,
        memory_type: str = "preference"
    ) -> None:
        """Store important information in long-term memory.
        
        Args:
            session_id: Session identifier.
            memory_text: Text to remember.
            memory_type: Type of memory (preference, fact, etc.).
        """
        if not settings.enable_long_term_memory:
            return
        
        logger.info(f"Storing long-term memory for session {session_id}")
        
        self.qdrant.store_memory(
            session_id=session_id,
            memory_text=memory_text,
            memory_type=memory_type,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "source": "conversation"
            }
        )
    
    def retrieve_long_term_memory(
        self,
        session_id: str,
    query: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """Retrieve relevant long-term memories.
        
        Args:
            session_id: Session identifier.
            query: Optional query to search memories.
            top_k: Number of memories to retrieve.
            
        Returns:
            Formatted memory context.
        """
        if not settings.enable_long_term_memory:
            return ""
        
        try:
            memories = self.qdrant.retrieve_memory(
                session_id=session_id,
                query=query,
                top_k=top_k
            )
        except Exception as e:
            logger.error(f"Failed to retrieve long-term memory from Qdrant: {e}")
            memories = []
        
        if not memories:
            return ""
        
        # Format memories
        memory_texts = [m.get("text", "") for m in memories]
        return "\n".join(f"- {text}" for text in memory_texts if text)
    
    def update_preferences(
        self,
        session_id: str,
        preferences: Dict[str, Any]
    ) -> None:
        """Update user preferences.
        
        Args:
            session_id: Session identifier.
            preferences: Preference dictionary.
        """
        session = self.get_session(session_id)
        session["user_preferences"].update(preferences)
        
        # Also store in long-term memory
        pref_text = json.dumps(preferences, indent=2)
        self.store_long_term_memory(
            session_id=session_id,
            memory_text=f"User preferences: {pref_text}",
            memory_type="preference"
        )
        
        logger.info(f"Updated preferences for session {session_id}")
    
    def get_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences.
        
        Args:
            session_id: Session identifier.
            
        Returns:
            Preferences dictionary.
        """
        session = self.get_session(session_id)
        return session.get("user_preferences", {})
    
    def store_clarified_intent(
        self,
        session_id: str,
        original_query: str,
        clarifications: Dict[str, str]
    ) -> None:
        """Store clarified intent from Q&A.
        
        Args:
            session_id: Session identifier.
            original_query: Original user query.
            clarifications: Clarification responses.
        """
        session = self.get_session(session_id)
        session["clarified_intent"][original_query] = {
            "clarifications": clarifications,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Stored clarified intent for session {session_id}")
    
    def get_clarified_intent(
        self,
        session_id: str,
    query: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get clarified intent.
        
        Args:
            session_id: Session identifier.
            query: Optional specific query.
            
        Returns:
            Clarified intent data.
        """
        session = self.get_session(session_id)
        clarified = session.get("clarified_intent", {})
        
        if query:
            return clarified.get(query, {})
        
        return clarified
    
    def _summarize_old_history(self, session: Dict[str, Any]) -> None:
        """Summarize old conversation history.
        
        Args:
            session: Session data.
        """
        history = session.get("conversation_history", [])
        
        if len(history) <= settings.summarization_threshold:
            return
        
        # Simple summarization: keep only key facts
        # In production, use LLM to summarize
        old_messages = history[:-settings.summarization_threshold]
        
        # Extract key information
        summary_parts = []
        for msg in old_messages:
            if msg.get("role") == "user":
                # Keep user queries
                summary_parts.append(f"User asked: {msg.get('content', '')[:100]}")
        
        # Store summary
        if summary_parts:
            summary = "\n".join(summary_parts[:5])  # Keep last 5
            session["history_summary"] = summary
        
        # Remove old messages
        session["conversation_history"] = history[-settings.summarization_threshold:]
        
        logger.info(f"Summarized history for session {session['session_id']}")
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions.
        
        Returns:
            Number of sessions cleaned up.
        """
        expired = []
        now = datetime.now()
        
        for session_id, session in self.sessions.items():
            last_activity = session.get("last_activity")
            if last_activity and now - last_activity > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.sessions[session_id]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        
        return len(expired)


# Singleton instance
memory_agent = MemoryAgent()
