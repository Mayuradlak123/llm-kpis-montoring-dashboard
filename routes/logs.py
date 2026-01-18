"""
API routes for log ingestion.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import random
import uuid

from config.logger import logger

from models.log_models import APILogRequest
from models.response_models import LogIngestionResponse
from workflows.monitoring_graph import process_log


router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("", response_model=LogIngestionResponse)
async def ingest_log(
    log_request: APILogRequest,
    background_tasks: BackgroundTasks
) -> LogIngestionResponse:
    """
    Ingest an API log for analysis.
    
    This endpoint triggers the complete LangGraph workflow:
    - Validates input
    - Extracts KPIs
    - Analyzes with LLM
    - Detects anomalies
    - Stores in MongoDB and Pinecone
    
    Returns analysis results and anomaly detection.
    """
    try:
        # Convert Pydantic model to dict
        log_data = log_request.model_dump()
        
        # Process through LangGraph workflow
        result = await process_log(log_data)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Log processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Return response
        return LogIngestionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Log ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_logs(
    limit: int = 100,
    endpoint: str | None = None
) -> Dict[str, Any]:
    """Get recent logs with optional endpoint filter."""
    try:
        from database.mongodb import mongodb_client
        
        logs = await mongodb_client.get_recent_logs(limit=limit, endpoint=endpoint)
        
        # Convert ObjectId to string
        for log in logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
        
        return {
            "success": True,
            "count": len(logs),
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch recent logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=LogIngestionResponse)
async def generate_synthetic_log():
    """
    Generate and process a synthetic API log.
    Useful for testing without an external generator.
    """
    endpoints = [
        "/api/v1/generate-email",
        "/api/v1/summarize-text",
        "/api/v1/translate",
        "/api/v1/chat",
        "/api/v1/code-completion"
    ]
    methods = ["POST", "GET"]
    status_codes = [200, 200, 200, 201, 400, 401, 403, 404, 500]
    
    # Generate random data
    endpoint = random.choice(endpoints)
    method = random.choice(methods)
    status = random.choice(status_codes)
    
    # Simulate latency (higher for errors or complex endpoints)
    base_latency = random.uniform(50, 500)
    if status >= 500:
        base_latency += random.uniform(500, 2000)
    
    log_data = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status,
        "latency": base_latency,
        "request_size": random.randint(100, 5000),
        "response_size": random.randint(100, 10000),
        "user_id": f"user_{random.randint(1, 100)}",
        "trace_id": str(uuid.uuid4())
    }
    
    # Add error message for failed requests
    if status >= 400:
        errors = [
            "Invalid API key",
            "Rate limit exceeded",
            "Internal server error",
            "Database connection failed",
            "validation error: missing field 'content'"
        ]
        log_data["error"] = random.choice(errors)
    
    logger.info(f"Generated synthetic log: {endpoint} ({status})")
    
    # Process the log through the workflow
    result = await process_log(log_data)
    
    return LogIngestionResponse(**result)
