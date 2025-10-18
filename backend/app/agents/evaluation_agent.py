"""
Evaluation Agent - Validates responses for hallucination and relevance.
"""
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import re

from app.config import settings

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """Agent responsible for evaluating response quality."""
    
    def __init__(self):
        """Initialize evaluation agent."""
        self.enabled = settings.enable_evaluation
        self.hallucination_threshold = settings.hallucination_threshold
        self.relevance_threshold = settings.relevance_threshold
        logger.info("EvaluationAgent initialized")
    
    def evaluate_response(
        self,
        query: str,
        response: str,
        retrieved_context: str = "",
        web_context: str = ""
    ) -> Dict[str, Any]:
        """Evaluate a generated response.
        
        Args:
            query: Original user query.
            response: Generated response.
            retrieved_context: Context from retrieval.
            web_context: Context from web scraping.
            
        Returns:
            Evaluation metrics dictionary.
        """
        if not self.enabled:
            return {"enabled": False}
        
        logger.info("Evaluating response quality")
        
        # Calculate various metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:100],
            "response_length": len(response),
            "hallucination_score": self._check_hallucination(
                response, retrieved_context, web_context
            ),
            "relevance_score": self._check_relevance(query, response),
            "context_usage_score": self._check_context_usage(
                response, retrieved_context, web_context
            ),
            "genai_focus_score": self._check_genai_focus(response),
            "citation_score": self._check_citations(response),
        }
        
        # Overall quality score
        metrics["overall_score"] = (
            0.3 * metrics["hallucination_score"] +
            0.3 * metrics["relevance_score"] +
            0.2 * metrics["context_usage_score"] +
            0.1 * metrics["genai_focus_score"] +
            0.1 * metrics["citation_score"]
        )
        
        # Pass/fail flags
        metrics["passed_hallucination_check"] = (
            metrics["hallucination_score"] >= self.hallucination_threshold
        )
        metrics["passed_relevance_check"] = (
            metrics["relevance_score"] >= self.relevance_threshold
        )
        metrics["overall_pass"] = (
            metrics["passed_hallucination_check"] and
            metrics["passed_relevance_check"]
        )
        
        logger.info(f"Evaluation complete. Overall score: {metrics['overall_score']:.2f}")
        return metrics
    
    def _check_hallucination(
        self,
        response: str,
        retrieved_context: str,
        web_context: str
    ) -> float:
        """Check for hallucination by comparing response with context.
        
        Args:
            response: Generated response.
            retrieved_context: Retrieved context.
            web_context: Web context.
            
        Returns:
            Score from 0-1 (higher is better, less hallucination).
        """
        # Simple heuristic: check if response contains info from context
        response_lower = response.lower()
        
        # Combine contexts
        full_context = f"{retrieved_context} {web_context}".lower()
        
        if not full_context.strip():
            # No context provided, can't check - give neutral score
            return 0.5
        
        # Check for common hallucination indicators
        hallucination_phrases = [
            "i don't have information",
            "i cannot verify",
            "i'm not sure",
            "to my knowledge",
            "as far as i know"
        ]
        
        has_disclaimer = any(phrase in response_lower for phrase in hallucination_phrases)
        
        # Extract key terms from response (simple approach)
        response_words = set(re.findall(r'\b\w{4,}\b', response_lower))
        context_words = set(re.findall(r'\b\w{4,}\b', full_context))
        
        # Calculate overlap
        if response_words:
            overlap = len(response_words & context_words) / len(response_words)
        else:
            overlap = 0.0
        
        # Score: higher overlap = less hallucination
        # Presence of disclaimer is good (honest)
        score = overlap * 0.8
        if has_disclaimer:
            score += 0.2
        
        return min(score, 1.0)
    
    def _check_relevance(self, query: str, response: str) -> float:
        """Check if response is relevant to query.
        
        Args:
            query: User query.
            response: Generated response.
            
        Returns:
            Relevance score from 0-1.
        """
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Extract key terms from query
        query_words = set(re.findall(r'\b\w{3,}\b', query_lower))
        response_words = set(re.findall(r'\b\w{3,}\b', response_lower))
        
        # Calculate relevance based on term overlap
        if query_words:
            relevance = len(query_words & response_words) / len(query_words)
        else:
            relevance = 0.0
        
        # Bonus for addressing the question directly
        question_indicators = ["what", "how", "why", "when", "where", "which"]
        if any(q in query_lower for q in question_indicators):
            # Check if response provides explanation
            explanation_indicators = ["because", "since", "therefore", "this means"]
            if any(exp in response_lower for exp in explanation_indicators):
                relevance += 0.1
        
        return min(relevance, 1.0)
    
    def _check_context_usage(
        self,
        response: str,
        retrieved_context: str,
        web_context: str
    ) -> float:
        """Check if context was effectively used.
        
        Args:
            response: Generated response.
            retrieved_context: Retrieved context.
            web_context: Web context.
            
        Returns:
            Context usage score from 0-1.
        """
        if not retrieved_context and not web_context:
            return 0.5  # Neutral if no context
        
        response_lower = response.lower()
        
        # Check for source citations
        citation_patterns = [
            r'according to',
            r'based on',
            r'source:',
            r'\[.*?\]',  # Markdown links
            r'research shows',
            r'studies indicate'
        ]
        
        has_citations = any(
            re.search(pattern, response_lower) for pattern in citation_patterns
        )
        
        # Check if specific info from context appears in response
        context_snippets = (retrieved_context + " " + web_context).split('.')
        
        overlap_count = 0
        for snippet in context_snippets[:10]:  # Check first 10 snippets
            snippet = snippet.strip().lower()
            if len(snippet) > 20 and snippet in response_lower:
                overlap_count += 1
        
        # Score based on citations and content overlap
        score = 0.0
        if has_citations:
            score += 0.5
        if overlap_count > 0:
            score += min(overlap_count * 0.1, 0.5)
        
        return min(score, 1.0)
    
    def _check_genai_focus(self, response: str) -> float:
        """Check if response focuses on GenAI topics.
        
        Args:
            response: Generated response.
            
        Returns:
            GenAI focus score from 0-1.
        """
        response_lower = response.lower()
        
        # Count GenAI keyword mentions
        keyword_count = sum(
            1 for kw in settings.genai_keywords if kw in response_lower
        )
        
        # Normalize by response length
        word_count = len(response.split())
        if word_count > 0:
            keyword_density = keyword_count / (word_count / 100)  # Per 100 words
        else:
            keyword_density = 0.0
        
        # Score based on keyword density
        score = min(keyword_density / 5.0, 1.0)  # 5+ keywords per 100 words = max score
        
        return score
    
    def _check_citations(self, response: str) -> float:
        """Check for proper citations and sources.
        
        Args:
            response: Generated response.
            
        Returns:
            Citation score from 0-1.
        """
        # Look for various citation formats
        citation_patterns = [
            r'\[Source \d+\]',
            r'\[.*?http.*?\]',
            r'Source:',
            r'According to',
            r'\(.*?\d{4}.*?\)',  # Year references
        ]
        
        citation_count = 0
        for pattern in citation_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            citation_count += len(matches)
        
        # Score based on number of citations
        if citation_count == 0:
            return 0.0
        elif citation_count == 1:
            return 0.5
        elif citation_count == 2:
            return 0.75
        else:
            return 1.0
    
    def format_metrics_summary(self, metrics: Dict[str, Any]) -> str:
        """Format metrics into a readable summary.
        
        Args:
            metrics: Evaluation metrics.
            
        Returns:
            Formatted summary string.
        """
        if not metrics.get("enabled", True):
            return "Evaluation disabled"
        
        summary = f"""
Evaluation Summary:
- Overall Score: {metrics.get('overall_score', 0):.2f}/1.00
- Hallucination Score: {metrics.get('hallucination_score', 0):.2f}/1.00 {'✓' if metrics.get('passed_hallucination_check') else '✗'}
- Relevance Score: {metrics.get('relevance_score', 0):.2f}/1.00 {'✓' if metrics.get('passed_relevance_check') else '✗'}
- Context Usage: {metrics.get('context_usage_score', 0):.2f}/1.00
- GenAI Focus: {metrics.get('genai_focus_score', 0):.2f}/1.00
- Citations: {metrics.get('citation_score', 0):.2f}/1.00
- Overall: {'PASS ✓' if metrics.get('overall_pass') else 'REVIEW ✗'}
"""
        return summary.strip()


# Singleton instance
evaluation_agent = EvaluationAgent()
