"""
Pydantic models for KPI metrics.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KPIMetrics(BaseModel):
    """Core KPI metrics for API monitoring."""
    
    # Request metrics
    total_requests: int = Field(..., description="Total number of requests")
    success_count: int = Field(..., description="Number of successful requests (2xx)")
    error_count: int = Field(..., description="Number of failed requests (4xx, 5xx)")
    
    # Rate metrics
    success_rate: float = Field(..., description="Success rate percentage", ge=0, le=100)
    error_rate: float = Field(..., description="Error rate percentage", ge=0, le=100)
    
    # Latency metrics
    avg_latency: float = Field(..., description="Average latency in ms", ge=0)
    p50_latency: float = Field(..., description="P50 latency in ms", ge=0)
    p95_latency: float = Field(..., description="P95 latency in ms", ge=0)
    p99_latency: float = Field(..., description="P99 latency in ms", ge=0)
    max_latency: float = Field(..., description="Maximum latency in ms", ge=0)
    
    # Time range
    time_range: str = Field(..., description="Time range (e.g., '1h', '24h')")
    start_time: datetime
    end_time: datetime
    
    # Optional endpoint filter
    endpoint: Optional[str] = Field(None, description="Filtered by endpoint")


class LLMMetrics(BaseModel):
    """LLM-specific metrics for cost and performance tracking."""
    
    total_llm_calls: int = Field(..., description="Total LLM API calls")
    total_input_tokens: int = Field(..., description="Total input tokens used")
    total_output_tokens: int = Field(..., description="Total output tokens generated")
    total_cost: float = Field(..., description="Total estimated cost in USD", ge=0)
    avg_llm_latency: float = Field(..., description="Average LLM latency in ms", ge=0)
    
    time_range: str
    start_time: datetime
    end_time: datetime


class AnomalyScore(BaseModel):
    """Anomaly detection metrics."""
    
    is_anomaly: bool = Field(..., description="Whether log is anomalous")
    severity: Optional[str] = Field(None, description="Severity level (LOW/MEDIUM/HIGH/CRITICAL)")
    confidence: float = Field(..., description="Confidence score", ge=0, le=1)
    reason: Optional[str] = Field(None, description="Reason for anomaly detection")
    detected_patterns: Optional[List[str]] = Field(None, description="Detected patterns")
    z_score: Optional[float] = Field(None, description="Statistical z-score")


class KPIDocument(BaseModel):
    """MongoDB document for aggregated KPI data."""
    
    # Metrics
    kpi_metrics: KPIMetrics
    llm_metrics: Optional[LLMMetrics] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    aggregation_type: str = Field(..., description="Type of aggregation (hourly, daily)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kpi_metrics": {
                    "total_requests": 1500,
                    "success_count": 1450,
                    "error_count": 50,
                    "success_rate": 96.67,
                    "error_rate": 3.33,
                    "avg_latency": 125.5,
                    "p95_latency": 250.0,
                    "time_range": "1h"
                }
            }
        }
