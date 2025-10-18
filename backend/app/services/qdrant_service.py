"""
Qdrant Vector Database Service.
Handles collection management, document ingestion, and hybrid search.
"""
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition,
    MatchValue, SearchRequest, QueryResponse, ScoredPoint
)
from qdrant_client.http.exceptions import UnexpectedResponse
import logging
import uuid

from app.config import settings
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Defer any network work; set fields only."""
        if self._initialized:
            return

        self.client: Optional[QdrantClient] = None
        self.knowledge_collection = settings.qdrant_collection
        self.memory_collection = settings.memory_collection
        # Do not connect yet; will connect on first use
        logger.info("QdrantService initialized (lazy mode)")
        # Cooldown control to avoid hammering on repeated failures
        self._last_connect_fail_ts = None
        self._connect_cooldown_seconds = 20  # seconds

    def _connect(self) -> bool:
        """Establish client connection with small retry loop."""
        if self.client is not None:
            return True

        tries = 0
        last_err: Optional[Exception] = None
        # Respect cooldown between attempts
        import time
        if self._last_connect_fail_ts is not None:
            since = time.time() - self._last_connect_fail_ts
            if since < self._connect_cooldown_seconds:
                logger.warning(
                    f"Skipping Qdrant connect attempt due to cooldown ({int(self._connect_cooldown_seconds - since)}s left)"
                )
                return False
        while tries < 3:
            tries += 1
            try:
                candidate = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    timeout=30,
                )
                # Lightweight call to verify connectivity
                candidate.get_collections()
                logger.info(f"Connected to Qdrant at {settings.qdrant_url}")
                # Only assign after successful connectivity check
                self.client = candidate
                self._ensure_collections()
                self._initialized = True
                return True
            except Exception as e:
                last_err = e
                logger.warning(f"Qdrant connect attempt {tries}/3 failed: {e}")
                # Ensure we don't keep a stale client on failure
                self.client = None
        # Record last failure timestamp for cooldown
        self._last_connect_fail_ts = time.time()
        logger.error(f"Failed to initialize Qdrant service after retries: {last_err}")
        return False

    def _ensure_client(self) -> bool:
        """Ensure client is connected before operations; return False if unavailable."""
        if self.client is None:
            return self._connect()
        return True
    
    def _ensure_collections(self):
        """Create collections if they don't exist."""
        if self.client is None:
            return
        collections = [self.knowledge_collection, self.memory_collection]
        
        for collection in collections:
            try:
                self.client.get_collection(collection)
                logger.info(f"Collection '{collection}' already exists")
            except (UnexpectedResponse, Exception):
                logger.info(f"Creating collection '{collection}'")
                self.client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
    
    def add_documents(
        self,
        texts: List[str],
        sources: Optional[List[str]] = None,
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        collection: Optional[str] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to the vector database.
        
        Args:
            texts: List of document texts.
            sources: List of source identifiers.
            metadata_list: List of metadata dicts for each document.
            collection: Collection name (defaults to knowledge collection).
            ids: Optional list of document IDs.
            
        Returns:
            List of document IDs.
        """
        collection = collection or self.knowledge_collection
        
        if not texts:
            logger.warning("No texts provided for ingestion")
            return []
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents")
        # Ensure client before computing embeddings to avoid wasted work if DB down
        self._ensure_client()
        embeddings = embedding_service.embed_texts(texts)
        
        # Prepare points
        points = []
        for i, (text, embedding, doc_id) in enumerate(zip(texts, embeddings, ids)):
            payload = {
                "text": text,
                "source": sources[i] if sources and i < len(sources) else "unknown"
            }
            # Add metadata if provided
            if metadata_list and i < len(metadata_list):
                payload.update(metadata_list[i])
            points.append(
                PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        # Upsert to Qdrant
        logger.info(f"Upserting {len(points)} points to collection '{collection}'")
        try:
            self._ensure_client()
            if self.client is not None:
                self.client.upsert(
                    collection_name=collection,
                    points=points
                )
            else:
                logger.error("Qdrant client is not connected; cannot upsert points.")
        except Exception as e:
            logger.error(f"Qdrant upsert failed: {e}")
        return ids
    
    def search(
        self,
        query: str,
        collection: Optional[str] = None,
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector search.
        
        Args:
            query: Search query text.
            collection: Collection to search.
            top_k: Number of results to return.
            filters: Optional filters for search.
            
        Returns:
            List of search results with scores.
        """
        collection = collection or self.knowledge_collection
        top_k = top_k or settings.retrieval_top_k
        # Generate query embedding
        self._ensure_client()
        query_embedding = embedding_service.embed_text(query)
        # Build filter if provided
        search_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)
        # Perform search
        self._ensure_client()
        try:
            if self.client is not None:
                results = self.client.search(
                    collection_name=collection,
                    query_vector=query_embedding,
                    limit=top_k,
                    query_filter=search_filter
                )
            else:
                logger.error("Qdrant client is not connected; cannot perform search.")
                results = []
        except Exception as e:
            logger.error(f"Qdrant search failed: {e}")
            results = []
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "source": result.payload.get("source", ""),
                "metadata": {k: v for k, v in result.payload.items() if k not in ["text", "source"]}
            })
        logger.info(f"Found {len(formatted_results)} results for query")
        return formatted_results
    
    def hybrid_search(
        self,
        query: str,
        keywords: Optional[List[str]] = None,
        collection: Optional[str] = None,
        top_k: Optional[int] = None,
        vector_weight: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and keyword search.
        
        Args:
            query: Search query text.
            keywords: Optional keywords for filtering.
            collection: Collection to search.
            top_k: Number of results to return.
            vector_weight: Weight for vector search (0-1).
            
        Returns:
            List of search results with combined scores.
        """
        collection = collection or self.knowledge_collection
        top_k = top_k or settings.retrieval_top_k
        vector_weight = vector_weight or settings.hybrid_search_weight
        keyword_weight = 1.0 - vector_weight
        # Perform vector search
        vector_results = self.search(query, collection, top_k * 2)
        # Simple hybrid: combine with keyword filtering
        if keywords:
            # Filter results containing keywords
            keyword_scores = {}
            for result in vector_results:
                text_lower = result["text"].lower()
                keyword_count = sum(1 for kw in keywords if kw.lower() in text_lower)
                keyword_scores[result["id"]] = keyword_count / max(len(keywords), 1)
        else:
            keyword_scores = {r["id"]: 0.0 for r in vector_results}
        # Combine scores
        for result in vector_results:
            vector_score = result["score"]
            keyword_score = keyword_scores.get(result["id"], 0.0)
            result["combined_score"] = (
                vector_weight * vector_score + keyword_weight * keyword_score
            )
        # Sort by combined score and return top_k
        vector_results.sort(key=lambda x: x["combined_score"], reverse=True)
        return vector_results[:top_k]
    
    def store_memory(
        self,
        session_id: str,
        memory_text: str,
        memory_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store user memory in long-term memory collection.
        
        Args:
            session_id: User session identifier.
            memory_text: Text to store.
            memory_type: Type of memory (conversation, preference, etc.).
            metadata: Additional metadata.
            
        Returns:
            Memory document ID.
        """
        self._ensure_client()
        payload = {
            "session_id": session_id,
            "text": memory_text,
            "type": memory_type
        }
        if metadata:
            payload.update(metadata)
        memory_id = str(uuid.uuid4())
        embedding = embedding_service.embed_text(memory_text)
        self._ensure_client()
        try:
            if self.client is not None:
                self.client.upsert(
                    collection_name=self.memory_collection,
                    points=[
                        PointStruct(
                            id=memory_id,
                            vector=embedding,
                            payload=payload
                        )
                    ]
                )
            else:
                logger.error("Qdrant client is not connected; cannot upsert memory.")
        except Exception as e:
            logger.error(f"Qdrant memory upsert failed: {e}")
        logger.info(f"Stored memory for session {session_id}")
        return memory_id
    
    def retrieve_memory(
        self,
        session_id: str,
        query: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve memories for a session.
        
        Args:
            session_id: User session identifier.
            query: Optional query to search memories.
            top_k: Number of memories to retrieve.
            
        Returns:
            List of memory documents.
        """
        self._ensure_client()
        if query:
            # Search by query similarity
            filters = {"session_id": session_id}
            return self.search(query, self.memory_collection, top_k, filters)
        else:
            # Retrieve all memories for session (simplified - in production use scroll)
            filters = {"session_id": session_id}
            # For now, use a generic query
            return self.search(session_id, self.memory_collection, top_k, filters)
    
    def get_collection_info(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a collection.
        
        Args:
            collection: Collection name.
            
        Returns:
            Collection information.
        """
        self._ensure_client()
        collection = collection or self.knowledge_collection
        try:
            if self.client is not None:
                info = self.client.get_collection(collection)
                return {
                    "name": collection,
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                    "status": info.status
                }
        except Exception as e:
            logger.error(f"Qdrant get_collection failed: {e}")
        return {}


# Singleton instance
qdrant_service = QdrantService()
