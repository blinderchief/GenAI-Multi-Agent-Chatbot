"""
Retrieval Agent - Queries Qdrant vector database for relevant GenAI knowledge.
"""
from typing import List, Dict, Any, Optional
import logging

from app.services.qdrant_service import qdrant_service
from app.config import settings

logger = logging.getLogger(__name__)


class RetrievalAgent:
    """Agent responsible for retrieving relevant documents from knowledge base."""
    
    def __init__(self):
        """Initialize retrieval agent."""
        self.qdrant = qdrant_service
        logger.info("RetrievalAgent initialized")
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        use_hybrid: bool = True,
        keywords: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: User query.
            top_k: Number of results to retrieve.
            use_hybrid: Whether to use hybrid search.
            keywords: Optional keywords for hybrid search.
            
        Returns:
            List of retrieved documents with scores.
        """
        top_k = top_k or settings.retrieval_top_k
        
        logger.info(f"Retrieving documents for query: '{query[:50]}...'")
        
        try:
            if use_hybrid and keywords:
                # Use hybrid search
                results = self.qdrant.hybrid_search(
                    query=query,
                    keywords=keywords,
                    top_k=top_k
                )
                logger.info(f"Hybrid search returned {len(results)} results")
            else:
                # Use standard vector search
                results = self.qdrant.search(
                    query=query,
                    top_k=top_k
                )
                logger.info(f"Vector search returned {len(results)} results")
            
            return results
        
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract potential keywords from query for hybrid search.
        
        Args:
            query: User query.
            
        Returns:
            List of extracted keywords.
        """
        # Simple keyword extraction - match against known GenAI terms
        query_lower = query.lower()
        keywords = []
        
        for term in settings.genai_keywords:
            if term in query_lower:
                keywords.append(term)
        
        # Also extract potential tool/framework names (capitalized words)
        words = query.split()
        for word in words:
            if word and word[0].isupper() and len(word) > 2:
                keywords.append(word)
        
        logger.info(f"Extracted keywords: {keywords}")
        return keywords
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """Format retrieved results into context string.
        
        Args:
            results: Retrieved documents.
            
        Returns:
            Formatted context string.
        """
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            text = result.get("text", "")
            source = result.get("source", "unknown")
            score = result.get("combined_score") or result.get("score", 0.0)
            
            context_parts.append(
                f"[Source {i}: {source} (relevance: {score:.2f})]\n{text}\n"
            )
        
        return "\n".join(context_parts)
    
    def is_relevant(self, query: str, threshold: float = 0.3) -> bool:
        """Check if query is relevant to GenAI domain.
        
        Args:
            query: User query.
            threshold: Minimum keyword match threshold.
            
        Returns:
            True if query appears GenAI-related.
        """
        query_lower = query.lower()
        
        # Count matching keywords
        matches = sum(1 for kw in settings.genai_keywords if kw in query_lower)
        
        # Calculate relevance score
        relevance_score = matches / max(len(settings.genai_keywords), 1)
        
        is_relevant = relevance_score >= threshold or matches >= 2
        logger.info(f"Query relevance: {relevance_score:.2f} (matches: {matches})")
        
        return is_relevant


# Singleton instance
retrieval_agent = RetrievalAgent()
