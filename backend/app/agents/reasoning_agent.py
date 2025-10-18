"""
Reasoning Agent - Synthesizes information and generates responses using LLM.
"""
from typing import List, Dict, Any, Optional
import logging

from app.services.llm_service import llm_service, ModelComplexity
from app.config import settings

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """Agent responsible for reasoning and response generation."""
    
    def __init__(self):
        """Initialize reasoning agent."""
        self.llm = llm_service
        self.persona_name = settings.persona_name
        self.persona_role = settings.persona_role
        logger.info("ReasoningAgent initialized")
    
    def generate_response(
        self,
        query: str,
        retrieved_context: str = "",
        web_context: str = "",
        user_memory: str = "",
        conversation_history: List[Dict[str, str]] = None,
        is_complex: bool = False
    ) -> str:
        """Generate response based on query and context.
        
        Args:
            query: User query.
            retrieved_context: Context from retrieval agent.
            web_context: Context from web scraper.
            user_memory: User's memory/preferences.
            conversation_history: Recent conversation history.
            is_complex: Whether to use complex model.
            
        Returns:
            Generated response.
        """
        logger.info(f"Generating response for query: '{query[:50]}...'")
        
        # Build comprehensive prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            query=query,
            retrieved_context=retrieved_context,
            web_context=web_context,
            user_memory=user_memory,
            conversation_history=conversation_history
        )
        
        # Compress if needed
        if settings.enable_prompt_compression:
            user_prompt = self.llm.compress_prompt(user_prompt)
        
        # Determine model complexity
        complexity = ModelComplexity.COMPLEX if is_complex else ModelComplexity.SIMPLE
        
        # Generate response
        response = self.llm.generate(
            prompt=user_prompt,
            complexity=complexity,
            temperature=0.7,
            max_tokens=2000,
            system_prompt=system_prompt
        )
        
        return response
    
    def generate_clarifying_questions(
        self,
        query: str,
        num_questions: int = None
    ) -> List[str]:
        """Generate clarifying questions for a user query.
        
        Args:
            query: User query.
            num_questions: Number of questions to generate.
            
        Returns:
            List of clarifying questions.
        """
        num_questions = num_questions or settings.min_clarifying_questions
        
        logger.info(f"Generating {num_questions} clarifying questions")
        
        prompt = f"""As {self.persona_name}, a {self.persona_role}, I need to ask {num_questions} clarifying questions about this user query to provide the best answer:

User Query: "{query}"

Generate exactly {num_questions} thoughtful clarifying questions that will help me understand:
1. The user's specific intent and use case
2. Their technical level and familiarity with the topic
3. Any constraints or preferences they have

Format each question on a new line starting with "Q:" 
Be conversational, friendly, and genuinely curious."""

        response = self.llm.generate(
            prompt=prompt,
            complexity=ModelComplexity.SIMPLE,
            temperature=0.8,
            max_tokens=500
        )
        
        # Parse questions from response
        questions = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('Q:'):
                question = line[2:].strip()
                if question:
                    questions.append(question)
        
        # Ensure we have enough questions
        if len(questions) < num_questions:
            # Add default questions if needed
            default_questions = [
                "Can you provide more details about your specific use case?",
                "Are you looking for a theoretical explanation or practical implementation?",
                "Do you have any preference for specific tools or frameworks?"
            ]
            questions.extend(default_questions[:num_questions - len(questions)])
        
        return questions[:num_questions]
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with persona and guidelines.
        
        Returns:
            System prompt string.
        """
        return f"""You are {self.persona_name}, a {self.persona_role}.

Background: You are {settings.persona_age} years old with a {settings.persona_background}. You're passionate about Generative AI, including LLMs, diffusion models, and emerging AI technologies.

Interaction Style:
- Friendly, curious, and thoughtful
- Conversational and natural
- Always ground responses in retrieved knowledge and recent information
- Cite sources when possible
- Admit when you don't know something
- Stay focused on Generative AI topics

Expertise Areas:
- Core GenAI techniques (ML, DL, NLP, CV, Speech, Multimodal AI)
- LLMs: GPT, Gemini, LLaMA, Mistral, Claude
- Diffusion models: Stable Diffusion, DALL-E, Midjourney
- Tools & Frameworks: LangChain, LangGraph, Hugging Face, PyTorch
- Vector databases: Qdrant, Pinecone, ChromaDB
- RAG, prompt engineering, fine-tuning, deployment

Guidelines:
- Use retrieved context and web information to answer accurately
- Be specific and technical when appropriate
- Provide examples and practical insights
- If question is off-topic (not GenAI), politely redirect
- Never hallucinate - if unsure, say so"""
    
    def _build_user_prompt(
        self,
        query: str,
        retrieved_context: str,
        web_context: str,
        user_memory: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build user prompt with all context.
        
        Args:
            query: User query.
            retrieved_context: Retrieved knowledge.
            web_context: Web search results.
            user_memory: User memory.
            conversation_history: Chat history.
            
        Returns:
            Complete user prompt.
        """
        parts = []
        
        # Add conversation history if exists
        if conversation_history:
            history_text = self._format_history(conversation_history)
            parts.append(f"Previous conversation:\n{history_text}\n")
        
        # Add user memory if exists
        if user_memory and user_memory.strip():
            parts.append(f"What I remember about you:\n{user_memory}\n")
        
        # Add retrieved context
        if retrieved_context and retrieved_context.strip():
            parts.append(f"Relevant knowledge from my resources:\n{retrieved_context}\n")
        
        # Add web context
        if web_context and web_context.strip():
            parts.append(f"Recent web information:\n{web_context}\n")
        
        # Add current query
        parts.append(f"Current question: {query}\n")
        parts.append("Please provide a helpful, accurate response based on the above context.")
        
        return "\n".join(parts)
    
    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history.
        
        Args:
            history: List of message dicts.
            
        Returns:
            Formatted history string.
        """
        formatted = []
        for msg in history[-5:]:  # Last 5 messages
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(formatted)
    
    def is_complex_query(self, query: str) -> bool:
        """Determine if query requires complex model.
        
        Args:
            query: User query.
            
        Returns:
            True if complex model recommended.
        """
        # Indicators of complexity
        complexity_indicators = [
            "explain in detail", "architecture", "comparison", "pros and cons",
            "differences between", "how does", "why", "implement", "design",
            "best practices", "production", "scale"
        ]
        
        query_lower = query.lower()
        is_complex = any(indicator in query_lower for indicator in complexity_indicators)
        
        # Also consider query length
        word_count = len(query.split())
        if word_count > 20:
            is_complex = True
        
        logger.info(f"Query complexity: {'complex' if is_complex else 'simple'}")
        return is_complex


# Singleton instance
reasoning_agent = ReasoningAgent()
