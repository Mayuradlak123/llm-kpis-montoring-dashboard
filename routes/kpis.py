"""
API routes for KPI metrics.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from config.logger import logger

from models.response_models import KPIResponse
from services.kpi_service import kpi_service

router = APIRouter(prefix="/kpis", tags=["kpis"])


@router.get("", response_model=KPIResponse)
async def get_kpis(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d, 30d"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint")
) -> KPIResponse:
    """
    Get aggregated KPI metrics.
    
    Query Parameters:
    - time_range: Time range for aggregation (1h, 24h, 7d, 30d)
    - endpoint: Optional endpoint filter
    
    Returns:
    - Aggregated metrics including latency, error rates, success rates
    """
    try:
        kpi_metrics = await kpi_service.get_aggregated_kpis(
            time_range=time_range,
            endpoint=endpoint
        )
        
        return KPIResponse(
            success=True,
            kpi_metrics=kpi_metrics,
            message=f"KPIs for {time_range}"
        )
        
    except Exception as e:
        logger.error(f"Failed to get KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm-metrics")
async def get_llm_metrics(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d, 30d")
):
    """Get LLM usage and cost metrics."""
    try:
        llm_metrics = await kpi_service.get_llm_metrics(time_range=time_range)
        
        return {
            "success": True,
            "llm_metrics": llm_metrics.model_dump(),
            "message": f"LLM metrics for {time_range}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get LLM metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/breakdown")
async def get_endpoint_breakdown(
    time_range: str = Query("1h", description="Time range: 1h, 24h, 7d, 30d")
):
    """Get KPI metrics broken down by endpoint."""
    try:
        breakdown = await kpi_service.get_endpoint_breakdown(time_range=time_range)
        
        # Convert to serializable format
        breakdown_data = {
            endpoint: metrics.model_dump()
            for endpoint, metrics in breakdown.items()
        }
        
        return {
            "success": True,
            "breakdown": breakdown_data,
            "message": f"Endpoint breakdown for {time_range}"
        }
        
    except Exception as e:
        logger.error(f"Failed to get endpoint breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))
