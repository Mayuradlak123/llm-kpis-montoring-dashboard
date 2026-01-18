"""
Pinecone vector database client for semantic log search.
"""
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
import hashlib

from config.logger import logger
from utils.config import settings


class PineconeClient:
    """Pinecone client for storing and searching log embeddings."""
    
    def __init__(self):
        self.pc: Optional[Pinecone] = None
        self.index = None
        self.index_name = settings.pinecone_index_name
    
    async def connect(self):
        """Initialize Pinecone connection and create index if needed."""
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            
            # Check if index exists, create if not
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 embedding dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Pinecone: {e}")
            raise
    
    async def disconnect(self):
        """Close Pinecone connection."""
        logger.info("Pinecone connection closed")
    
    def generate_embedding_id(self, log_data: Dict[str, Any]) -> str:
        """Generate unique ID for embedding based on log data."""
        # Create hash from endpoint, timestamp, and trace_id
        unique_string = f"{log_data.get('endpoint')}_{log_data.get('timestamp')}_{log_data.get('trace_id', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    async def upsert_embedding(
        self,
        embedding_id: str,
        embedding_vector: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Store embedding in Pinecone.
        
        Args:
            embedding_id: Unique ID for the embedding
            embedding_vector: Vector representation of the log
            metadata: Associated metadata (endpoint, status, latency, etc.)
        
        Returns:
            True if successful
        """
        try:
            # Prepare metadata (Pinecone has restrictions on metadata types)
            clean_metadata = self._clean_metadata(metadata)
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": embedding_id,
                        "values": embedding_vector,
                        "metadata": clean_metadata
                    }
                ]
            )
            
            logger.debug(f"Upserted embedding: {embedding_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert embedding: {e}")
            return False
    
    async def search_similar_logs(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar logs using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of similar log matches with scores
        """
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"Failed to search similar logs: {e}")
            return []
    
    async def delete_embedding(self, embedding_id: str) -> bool:
        """Delete an embedding from Pinecone."""
        try:
            self.index.delete(ids=[embedding_id])
            logger.debug(f"Deleted embedding: {embedding_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete embedding: {e}")
            return False
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean metadata to comply with Pinecone requirements.
        Pinecone supports: strings, numbers, booleans, lists of strings.
        """
        clean = {}
        
        for key, value in metadata.items():
            # Skip None values
            if value is None:
                continue
            
            # Convert datetime to ISO string
            if hasattr(value, 'isoformat'):
                clean[key] = value.isoformat()
            # Keep primitives
            elif isinstance(value, (str, int, float, bool)):
                clean[key] = value
            # Convert lists
            elif isinstance(value, list):
                clean[key] = [str(item) for item in value]
            # Convert everything else to string
            else:
                clean[key] = str(value)
        
        return clean
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the Pinecone index."""
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Pinecone Index Stats: {stats.total_vector_count} vectors")
            return {
                "total_vector_count": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}


# Global Pinecone client instance
pinecone_client = PineconeClient()
