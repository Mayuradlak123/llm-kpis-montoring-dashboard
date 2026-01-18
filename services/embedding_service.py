"""
Embedding service for converting logs to vector representations.
Uses sentence-transformers for local embedding generation.
"""
from typing import List, Dict, Any
import os

from sentence_transformers import SentenceTransformer
from config.logger import logger

# Configuration
LOCAL_EMBED_MODEL = os.getenv("LOCAL_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Initialize embedding model
_embed_model = SentenceTransformer(LOCAL_EMBED_MODEL)


class EmbeddingService:
    """Service for generating embeddings from log data."""
    
    def __init__(self):
        self.model = _embed_model
        logger.info(f"Embedding service initialized with model: {LOCAL_EMBED_MODEL}")
    
    async def generate_embedding(self, log_data: Dict[str, Any]) -> List[float]:
        """
        Generate embedding vector from log data.
        
        Args:
            log_data: Dictionary containing log information
        
        Returns:
            Embedding vector (384 dimensions for all-mpnet-base-v2)
        """
        try:
            # Create text representation of log
            log_text = self._log_to_text(log_data)
            
            # Generate embedding using sentence-transformers
            embedding = embed_query(log_text)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 384
    
    def _log_to_text(self, log_data: Dict[str, Any]) -> str:
        """Convert log data to text for embedding."""
        parts = [
            f"Endpoint: {log_data.get('endpoint', 'unknown')}",
            f"Method: {log_data.get('method', 'unknown')}",
            f"Status: {log_data.get('status_code', 0)}",
            f"Latency: {log_data.get('latency', 0)}ms"
        ]
        
        if log_data.get('error'):
            parts.append(f"Error: {log_data['error']}")
        
        if log_data.get('llm_analysis'):
            parts.append(f"Analysis: {log_data['llm_analysis']}")
        
        return " | ".join(parts)
    
    async def batch_generate_embeddings(
        self,
        logs: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """Generate embeddings for multiple logs efficiently."""
        embeddings = []
        
        for log in logs:
            embedding = await self.generate_embedding(log)
            embeddings.append(embedding)
        
        return embeddings


def embed_query(text: str) -> List[float]:
    """
    Generate embedding for a text query.
    
    Args:
        text: Input text to embed
    
    Returns:
        Normalized embedding vector
    """
    return _embed_model.encode(text, normalize_embeddings=True).tolist()


# Global embedding service instance
embedding_service = EmbeddingService()

