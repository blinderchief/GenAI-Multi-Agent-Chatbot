"""
Chat Orchestrator - Coordinates all agents for the chatbot
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..models import ChatMessage, AgentResponse, ConversationState
from ..agents.retrieval_agent import RetrievalAgent
from ..agents.web_scraper_agent import WebScraperAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..agents.memory_agent import memory_agent
from ..agents.evaluation_agent import EvaluationAgent
from ..config import settings

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Orchestrates the multi-agent system for the chatbot.
    Coordinates: Retrieval → Web Scraping → Reasoning → Memory → Evaluation
    """

    def __init__(self):
        """Initialize all agents"""
        self.retrieval_agent = RetrievalAgent()
        self.web_scraper_agent = WebScraperAgent()
        self.reasoning_agent = ReasoningAgent()
        self.memory_agent = memory_agent
        self.evaluation_agent = EvaluationAgent()

        # Persona
        self.persona = {
            "name": settings.persona_name,
            "role": "Research Analyst specializing in Generative AI",
            "background": "28-year-old with a master's in CS from MIT, focusing on ML and NLP",
            "interests": [
                "AI libraries",
                "emerging GenAI models",
                "research papers",
                "industry trends",
            ],
            "style": "Friendly, curious, and thoughtful",
        }

        logger.info("ChatOrchestrator initialized with all agents")

    def _get_introduction(self) -> str:
        """Generate the assistant's introduction for new sessions"""
        return (
            f"Hi! I'm {self.persona['name']}, a GenAI enthusiast who loves diving into "
            f"the latest AI tools and research. What's the specific GenAI topic you're "
            f"curious about today? Are you looking for insights on a particular framework, "
            f"model, or something else?"
        )

    def _is_genai_related(self, query: str) -> bool:
        """
        Check if query is related to Generative AI topics.
        Topics: ML, DL, NLP, CV, Speech, Multimodal AI, GenAI tools, frameworks, research
        """
        genai_keywords = [
            "ai",
            "artificial intelligence",
            "machine learning",
            "ml",
            "deep learning",
            "dl",
            "neural network",
            "transformer",
            "gpt",
            "llm",
            "large language model",
            "generative",
            "genai",
            "nlp",
            "natural language",
            "computer vision",
            "cv",
            "diffusion",
            "gan",
            "stable diffusion",
            "midjourney",
            "dall-e",
            "dalle",
            "langchain",
            "langgraph",
            "hugging face",
            "pytorch",
            "tensorflow",
            "openai",
            "anthropic",
            "claude",
            "gemini",
            "llama",
            "mistral",
            "embedding",
            "vector",
            "rag",
            "retrieval",
            "chatbot",
            "chat",
            "speech",
            "tts",
            "text to speech",
            "whisper",
            "multimodal",
            "model",
            "training",
            "fine-tuning",
            "finetuning",
            "prompt",
            "agent",
            "automation",
            "qdrant",
            "pinecone",
            "weaviate",
            "research",
            "paper",
            "arxiv",
            "framework",
            "library",
            "tool",
            # Project/internals related
            "aria",
            "architecture",
            "orchestrator",
            "pipeline",
            "evaluation",
            "seed",
            "internal",
            "docs",
            "repository",
            "backend",
            "frontend",
            "fastapi",
            "streamlit",
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in genai_keywords)

    def _generate_redirect_message(self, query: str) -> str:
        """Generate a polite redirect message for non-GenAI queries"""
        return (
            f"That's an interesting question about '{query}', but I specialize specifically "
            f"in Generative AI topics like ML, DL, NLP, computer vision, speech AI, and "
            f"related tools and frameworks. Would you like to discuss something like "
            f"AI model training, frameworks like LangChain, or tools like Stable Diffusion instead?"
        )

    def _should_ask_clarifying_questions(
        self, query: str, conversation_state: ConversationState
    ) -> bool:
        """
        Determine if we should ask clarifying questions.
        Skip if user is answering previous clarifying questions.
        """
        # Check if last message was from Aria asking questions
        if conversation_state.messages:
            last_msg = conversation_state.messages[-1]
            if last_msg.role == "assistant" and "?" in last_msg.content:
                # User is likely responding to our questions
                return False

        # Ask clarifying questions for vague queries
        vague_indicators = [
            "tool",
            "framework",
            "model",
            "best",
            "how",
            "what",
            "which",
            "recommend",
        ]
        query_lower = query.lower()
        is_vague = any(indicator in query_lower for indicator in vague_indicators)

        # Check if we've already asked questions in this conversation
        questions_asked = conversation_state.context.get(
            "clarifying_questions_asked", 0
        )

        return is_vague and questions_asked < 1

    def _generate_clarifying_questions(self, query: str) -> str:
        """Generate 2-3 clarifying questions based on the query"""
        questions: List[str] = []

        query_lower = query.lower()

        # Question templates based on query content
        if "tool" in query_lower or "framework" in query_lower:
            questions.append(
                "Are you looking for tools for text generation, image synthesis, or something else?"
            )
            questions.append("Do you prefer open-source or commercial solutions?")

        if "model" in query_lower:
            questions.append(
                "Are you interested in language models, image generation models, or multimodal models?"
            )
            questions.append(
                "Is this for research, production use, or learning purposes?"
            )

        if "best" in query_lower or "recommend" in query_lower:
            questions.append("What's your primary use case or goal?")
            questions.append(
                "Do you have any specific requirements like model size, speed, or cost?"
            )

        if "how" in query_lower:
            questions.append(
                "Are you looking for a high-level overview or step-by-step implementation details?"
            )
            questions.append(
                "What's your current experience level with this topic?"
            )

        # Default questions if none matched
        if not questions:
            questions = [
                "Could you provide more context about what you're trying to achieve?",
                "Are you looking for practical implementation guidance or theoretical understanding?",
            ]

        # Return up to 3 questions
        return "Before I answer, let me clarify a few things:\n" + "\n".join(
            f"{i+1}. {q}" for i, q in enumerate(questions[:3])
        )

    async def process_message(
        self,
        message: ChatMessage,
        session_id: str,
        conversation_state: Optional[ConversationState] = None,
    ) -> AgentResponse:
        """
        Main orchestration method - coordinates all agents to process a user message.

        Flow:
        1. Check if new session → introduce Aria
        2. Validate GenAI relevance → redirect if needed
        3. Check if need clarifying questions → ask and return
        4. Retrieve from Qdrant (Retrieval Agent)
        5. Scrape web if needed (Web Scraper Agent)
        6. Synthesize response (Reasoning Agent)
        7. Update memory (Memory Agent)
        8. Evaluate response (Evaluation Agent)
        9. Return final response
        """
        logger.info(
            f"Processing message for session {session_id}: {message.content[:100]}"
        )

        # Load or create session (MemoryAgent stores raw dict history)
        session = self.memory_agent.get_session(session_id)
        history: List[Dict[str, str]] = session.get("conversation_history", [])

        # Step 1: Introduction for new sessions
        if not history:
            intro = self._get_introduction()
            # Store intro and user message
            self.memory_agent.add_message(session_id, "assistant", intro)
            self.memory_agent.add_message(
                session_id, message.role, message.content
            )

            return AgentResponse(
                content=intro,
                agent="orchestrator",
                confidence=1.0,
                sources=[],
                metadata={"type": "introduction"},
            )

        # Add user message to history
        self.memory_agent.add_message(session_id, message.role, message.content)

        # Step 2: Check GenAI relevance but don't early-return.
        # We still attempt retrieval/web; only redirect later if nothing is found.
        domain_ok = self._is_genai_related(message.content)

        # Step 3: Ask clarifying questions if needed
        pseudo_state = ConversationState(
            session_id=session_id,
            messages=[
                ChatMessage(
                    role=m.get("role", "user"), content=m.get("content", "")
                )
                for m in self.memory_agent.get_conversation_history(session_id)
            ],
            context={
                "clarifying_questions_asked": session.get(
                    "clarifying_questions_asked", 0
                ),
                **session.get("clarified_intent", {}),
            },
        )
        if self._should_ask_clarifying_questions(message.content, pseudo_state):
            clarifying = self._generate_clarifying_questions(message.content)
            session["clarifying_questions_asked"] = session.get(
                "clarifying_questions_asked", 0
            ) + 1
            self.memory_agent.add_message(session_id, "assistant", clarifying)

            return AgentResponse(
                content=clarifying,
                agent="orchestrator",
                confidence=1.0,
                sources=[],
                metadata={"type": "clarifying_questions"},
            )

        # Step 4: Retrieval from Qdrant
        logger.info("Step 4: Retrieving from Qdrant")
        results = self.retrieval_agent.retrieve(
            query=message.content, top_k=settings.retrieval_top_k
        )
        retrieval_context = self.retrieval_agent.format_context(results)

        # Step 5: Web scraping for fresh data (if needed)
        logger.info("Step 5: Web scraping")
        web_results = await self.web_scraper_agent.scrape_async(query=message.content)
        web_context = self.web_scraper_agent.format_results(web_results)

        # If nothing found and domain looks off-topic, provide a polite redirect now
        if not results and not web_results and not domain_ok:
            redirect = self._generate_redirect_message(message.content)
            self.memory_agent.add_message(session_id, "assistant", redirect)
            return AgentResponse(
                content=redirect,
                agent="orchestrator",
                confidence=1.0,
                sources=[],
                metadata={"type": "redirect", "reason": "no_context_and_off_domain"},
            )

        # Step 6: Reasoning and synthesis
        logger.info("Step 6: Reasoning and synthesis")
        is_complex = self.reasoning_agent.is_complex_query(message.content)
        response_text = self.reasoning_agent.generate_response(
            query=message.content,
            retrieved_context=retrieval_context,
            web_context=web_context,
            user_memory=self.memory_agent.retrieve_long_term_memory(session_id),
            conversation_history=self.memory_agent.get_conversation_history(
                session_id, limit=10
            ),
            is_complex=is_complex,
        )

        # Step 7: Update memory
        logger.info("Step 7: Updating memory")
        self.memory_agent.add_message(session_id, "assistant", response_text)

        # Step 8: Evaluation
        logger.info("Step 8: Evaluating response")
        metrics = self.evaluation_agent.evaluate_response(
            query=message.content,
            response=response_text,
            retrieved_context=retrieval_context,
            web_context=web_context,
        )

        # Combine metadata
        final_metadata = {
            "evaluation": metrics,
            "retrieval_sources": len(results),
            "web_sources": len(web_results),
        }

        # Combine sources
        all_sources: List[Dict[str, object]] = []
        for r in results:
            all_sources.append(
                {
                    "title": r.get("metadata", {}).get(
                        "title", r.get("source", "Qdrant")
                    ),
                    "url": r.get("metadata", {}).get("url", ""),
                    "type": "qdrant",
                    "relevance": r.get("combined_score", r.get("score", 0.0)),
                }
            )
        for w in web_results:
            all_sources.append(
                {
                    "title": w.get("title", "Web Result"),
                    "url": w.get("link", ""),
                    "type": w.get("source", "web"),
                    "relevance": 0.0,
                }
            )

        logger.info("Response generated")

        return AgentResponse(
            content=response_text,
            agent="orchestrator",
            confidence=metrics.get("overall_score", 0.7),
            sources=all_sources,
            metadata=final_metadata,
        )

    async def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Retrieve conversation history for a session"""
        history = self.memory_agent.get_conversation_history(session_id)
        return [
            ChatMessage(role=m.get("role", "user"), content=m.get("content", ""))
            for m in history
        ]

    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history for a session"""
        session = self.memory_agent.get_session(session_id)
        session["conversation_history"] = []
        session["message_count"] = 0
        return True
