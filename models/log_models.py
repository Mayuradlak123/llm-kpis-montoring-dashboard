"""
Pydantic models for API logs.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class APILogRequest(BaseModel):
    """Incoming API log data from external systems."""
    
    endpoint: str = Field(..., description="API endpoint path")
    method: str = Field(..., description="HTTP method (GET, POST, etc.)")
    status_code: int = Field(..., description="HTTP status code", ge=100, le=599)
    latency: float = Field(..., description="Request latency in milliseconds", ge=0)
    error: Optional[str] = Field(None, description="Error message if request failed")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    trace_id: Optional[str] = Field(None, description="Distributed tracing ID")
    headers: Optional[Dict[str, str]] = Field(None, description="Request headers")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class LogMetadata(BaseModel):
    """Additional context for API logs."""
    
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class APILogDocument(BaseModel):
    """MongoDB document schema for API logs."""
    
    # Original log data
    endpoint: str
    method: str
    status_code: int
    latency: float
    error: Optional[str] = None
    
    # Metadata
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Analysis results (populated by LangGraph)
    llm_analysis: Optional[str] = None
    is_anomaly: bool = False
    anomaly_score: float = 0.0
    anomaly_severity: Optional[str] = None
    anomaly_reason: Optional[str] = None
    
    # LLM metrics
    llm_tokens_input: int = 0
    llm_tokens_output: int = 0
    llm_cost: float = 0.0
    llm_latency: float = 0.0
    
    # Vector embedding ID (Pinecone)
    embedding_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "endpoint": "/api/users",
                "method": "GET",
                "status_code": 200,
                "latency": 145.5,
                "error": None,
                "timestamp": "2026-01-18T06:30:00Z",
                "is_anomaly": False
            }
        }
