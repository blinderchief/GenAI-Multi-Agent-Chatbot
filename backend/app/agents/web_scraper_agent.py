"""
Web Scraper Agent - Fetches real-time information from the web.
"""
from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class WebScraperAgent:
    """Agent responsible for fetching real-time web information."""
    
    def __init__(self):
        """Initialize web scraper agent."""
        self.max_results = settings.max_scrape_results
        self.timeout = settings.scraping_timeout
        logger.info("WebScraperAgent initialized")
    
    async def scrape_async(
        self,
        query: str,
    sources: Optional[List[str]] = None,
    max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Asynchronously scrape web for information.
        
        Args:
            query: Search query.
            sources: Optional list of specific sources to scrape.
            max_results: Maximum number of results.
            
        Returns:
            List of scraped results.
        """
        max_results = max_results or self.max_results
        
        logger.info(f"Scraping web for: '{query[:50]}...'")
        
        try:
            # Use SerpAPI if available
            if settings.serpapi_api_key:
                return await self._scrape_with_serpapi(query, max_results)
            else:
                # Fallback to mock data for development
                logger.warning("SerpAPI key not configured, using mock data")
                return self._get_mock_results(query, max_results)
        
        except Exception as e:
            logger.error(f"Error during web scraping: {e}")
            return []
    
    def scrape(
        self,
        query: str,
    sources: Optional[List[str]] = None,
    max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous wrapper for web scraping.
        
        Args:
            query: Search query.
            sources: Optional list of specific sources to scrape.
            max_results: Maximum number of results.
            
        Returns:
            List of scraped results.
        """
        try:
            asyncio.get_running_loop()
            # If there's already a running loop (e.g., inside FastAPI),
            # this sync API cannot block; fall back to mock or empty results.
            logger.warning("scrape() called inside running event loop; using mock results")
            return self._get_mock_results(query, max_results or self.max_results)
        except RuntimeError:
            # No running loop; safe to run normally
            return asyncio.run(self.scrape_async(query, sources, max_results))
    
    async def _scrape_with_serpapi(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Scrape using SerpAPI.
        
        Args:
            query: Search query.
            max_results: Maximum results.
            
        Returns:
            List of search results.
        """
        try:
            from serpapi import GoogleSearch
            
            params = {
                "q": query,
                "api_key": settings.serpapi_api_key,
                "num": max_results,
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract organic results
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for result in organic_results[:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", ""),
                    "source": "web",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"SerpAPI returned {len(formatted_results)} results")
            return formatted_results
        
        except ImportError:
            logger.error("SerpAPI library not installed")
            return self._get_mock_results(query, max_results)
        except Exception as e:
            logger.error(f"SerpAPI error: {e}")
            return self._get_mock_results(query, max_results)
    
    def _get_mock_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generate mock search results for development.
        
        Args:
            query: Search query.
            max_results: Maximum results.
            
        Returns:
            List of mock results.
        """
        mock_results = [
            {
                "title": f"Latest in {query} - Research Update",
                "snippet": f"Recent developments in {query} show significant progress in the field of Generative AI...",
                "link": "https://example.com/research",
                "source": "web_mock",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "title": f"{query} Best Practices - Developer Guide",
                "snippet": f"A comprehensive guide to implementing {query} in production environments...",
                "link": "https://example.com/guide",
                "source": "web_mock",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "title": f"{query} Trends and Analysis",
                "snippet": f"Industry analysis of {query} trends and future predictions for AI development...",
                "link": "https://example.com/analysis",
                "source": "web_mock",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        return mock_results[:max_results]
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format scraped results into context string.
        
        Args:
            results: Scraped results.
            
        Returns:
            Formatted context string.
        """
        if not results:
            return "No recent web information found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "Unknown")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            context_parts.append(
                f"[Web Result {i}: {title}]\n{snippet}\nSource: {link}\n"
            )
        
        return "\n".join(context_parts)
    
    def should_scrape(self, query: str) -> bool:
        """Determine if web scraping is needed for this query.
        
        Args:
            query: User query.
            
        Returns:
            True if web scraping would be beneficial.
        """
        # Keywords that suggest need for current information
        time_sensitive_keywords = [
            "latest", "recent", "new", "current", "update", "2024", "2025",
            "trending", "news", "announcement", "release"
        ]
        
        query_lower = query.lower()
        should_scrape = any(kw in query_lower for kw in time_sensitive_keywords)
        
        logger.info(f"Should scrape: {should_scrape} for query: '{query[:50]}...'")
        return should_scrape


# Singleton instance
web_scraper_agent = WebScraperAgent()
