"""
Embedding Service using sentence-transformers.
Generates embeddings for text documents and queries.
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings."""
    
    def __init__(self, model_name: str = None):
        """Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence-transformer model to use.
        """
        self.model_name = model_name or settings.embedding_model
        self._model = None
        logger.info(f"Initializing EmbeddingService with model: {self.model_name}")
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text to embed.
            
        Returns:
            List of floats representing the embedding vector.
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return [0.0] * settings.embedding_dimension
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * settings.embedding_dimension
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed.
            batch_size: Batch size for encoding.
            
        Returns:
            List of embedding vectors.
        """
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [[0.0] * settings.embedding_dimension] * len(texts)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts.
        
        Args:
            text1: First text.
            text2: Second text.
            
        Returns:
            Similarity score between 0 and 1.
        """
        emb1 = np.array(self.embed_text(text1))
        emb2 = np.array(self.embed_text(text2))
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def get_dimension(self) -> int:
        """Get the embedding dimension.
        
        Returns:
            Dimension of the embedding vectors.
        """
        return self.model.get_sentence_embedding_dimension()


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()


# Export singleton instance
embedding_service = get_embedding_service()
