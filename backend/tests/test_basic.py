"""
Test suite for Aria Chatbot
"""
import pytest
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models import ChatMessage, AgentResponse, ConversationState
from datetime import datetime


class TestModels:
    """Test Pydantic models"""
    
    def test_chat_message_creation(self):
        """Test creating a ChatMessage"""
        msg = ChatMessage(
            role="user",
            content="What is LangChain?",
            timestamp=datetime.utcnow()
        )
        assert msg.role == "user"
        assert msg.content == "What is LangChain?"
        assert isinstance(msg.timestamp, datetime)
    
    def test_agent_response_creation(self):
        """Test creating an AgentResponse"""
        response = AgentResponse(
            content="LangChain is a framework...",
            agent="reasoning",
            confidence=0.95,
            sources=[],
            metadata={"test": "value"}
        )
        assert response.content == "LangChain is a framework..."
        assert response.agent == "reasoning"
        assert response.confidence == 0.95
        assert response.sources == []
        assert response.metadata == {"test": "value"}
    
    def test_conversation_state_creation(self):
        """Test creating a ConversationState"""
        state = ConversationState(
            session_id="test-123",
            messages=[],
            metadata={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        assert state.session_id == "test-123"
        assert len(state.messages) == 0
        assert isinstance(state.created_at, datetime)


class TestChatOrchestrator:
    """Test ChatOrchestrator"""
    
    def test_genai_query_detection(self):
        """Test detection of GenAI-related queries"""
        from app.pipelines.chat_orchestrator import ChatOrchestrator
        
        orchestrator = ChatOrchestrator()
        
        # Should be detected as GenAI
        assert orchestrator._is_genai_related("What is LangChain?")
        assert orchestrator._is_genai_related("How do I use GPT-4?")
        assert orchestrator._is_genai_related("Tell me about diffusion models")
        assert orchestrator._is_genai_related("What are transformers in ML?")
        
        # Should NOT be detected as GenAI
        assert not orchestrator._is_genai_related("What's the weather today?")
        assert not orchestrator._is_genai_related("How do I cook pasta?")
        assert not orchestrator._is_genai_related("Who won the game?")
    
    def test_persona_info(self):
        """Test persona information"""
        from app.pipelines.chat_orchestrator import ChatOrchestrator
        
        orchestrator = ChatOrchestrator()
        
        assert orchestrator.persona["name"] == "Aria Voss"
        assert "Research Analyst" in orchestrator.persona["role"]
        assert isinstance(orchestrator.persona["interests"], list)
        assert len(orchestrator.persona["interests"]) > 0


class TestConfig:
    """Test configuration"""
    
    def test_config_loading(self):
        """Test that config loads properly"""
        from app.config import settings
        
        assert settings.PROJECT_NAME == "Aria - GenAI Chatbot"
        assert hasattr(settings, "LLM_PROVIDER")
        assert hasattr(settings, "QDRANT_URL")
        assert hasattr(settings, "BACKEND_PORT")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
