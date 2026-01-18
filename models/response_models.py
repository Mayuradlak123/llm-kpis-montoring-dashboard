"""
Pydantic models for API responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .kpi_models import KPIMetrics, AnomalyScore


class LogIngestionResponse(BaseModel):
    """Response after log ingestion."""
    
    success: bool = Field(..., description="Whether ingestion was successful")
    log_id: str = Field(..., description="MongoDB document ID")
    analysis_summary: Optional[str] = Field(None, description="LLM analysis summary")
    is_anomaly: bool = Field(..., description="Whether log is anomalous")
    anomaly_severity: Optional[str] = Field(None, description="Anomaly severity level")
    processing_time_ms: float = Field(..., description="Total processing time in ms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "log_id": "65a1b2c3d4e5f6g7h8i9j0k1",
                "analysis_summary": "Normal request. Latency within expected range.",
                "is_anomaly": False,
                "processing_time_ms": 234.5
            }
        }


class KPIResponse(BaseModel):
    """Response for KPI aggregation queries."""
    
    success: bool = True
    kpi_metrics: KPIMetrics
    message: Optional[str] = None


class AnomalyResponse(BaseModel):
    """Response for anomaly queries."""
    
    log_id: str
    endpoint: str
    method: str
    status_code: int
    latency: float
    timestamp: datetime
    
    # Anomaly details
    anomaly_score: AnomalyScore
    llm_analysis: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "log_id": "65a1b2c3d4e5f6g7h8i9j0k1",
                "endpoint": "/api/checkout",
                "method": "POST",
                "status_code": 500,
                "latency": 5000.0,
                "timestamp": "2026-01-18T06:30:00Z",
                "anomaly_score": {
                    "is_anomaly": True,
                    "severity": "CRITICAL",
                    "confidence": 0.95,
                    "reason": "Latency 10x above P95, server error"
                }
            }
        }


class AnomalyListResponse(BaseModel):
    """Response for listing anomalies."""
    
    success: bool = True
    total_count: int
    anomalies: List[AnomalyResponse]
    time_range: str
    message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict = Field(default_factory=dict)
