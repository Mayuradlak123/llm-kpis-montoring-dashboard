"""
API routes for anomaly detection.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from config.logger import logger

from models.response_models import AnomalyListResponse
from services.anomaly_service import anomaly_service

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.get("", response_model=AnomalyListResponse)
async def get_anomalies(
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d, 30d"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results")
) -> AnomalyListResponse:
    """
    Get detected anomalies.
    
    Query Parameters:
    - severity: Filter by severity level (LOW, MEDIUM, HIGH, CRITICAL)
    - time_range: Time range for query
    - limit: Maximum number of results (1-500)
    
    Returns:
    - List of anomalies with LLM analysis and severity scores
    """
    try:
        anomalies = await anomaly_service.get_anomalies(
            severity=severity,
            time_range=time_range,
            limit=limit
        )
        
        return AnomalyListResponse(
            success=True,
            total_count=len(anomalies),
            anomalies=anomalies,
            time_range=time_range,
            message=f"Found {len(anomalies)} anomalies"
        )
        
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def get_anomaly_count(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d, 30d")
):
    """Get count of anomalies in time range."""
    try:
        from database.mongodb import mongodb_client
        from utils.metrics import time_range_to_datetime
        
        start_time, end_time = time_range_to_datetime(time_range)
        count = await mongodb_client.get_anomaly_count(start_time, end_time)
        
        return {
            "success": True,
            "count": count,
            "time_range": time_range
        }
        
    except Exception as e:
        logger.error(f"Failed to get anomaly count: {e}")
        raise HTTPException(status_code=500, detail=str(e))
