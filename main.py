"""
Main FastAPI application.
Bootstrap and wire all components.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from config.logger import logger
from database.mongodb import mongodb_client
from database.pinecone_client import pinecone_client
from routes import logs_router, kpis_router, anomalies_router, websocket_router
from models.response_models import HealthCheckResponse
from utils.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting LLM KPI Monitoring System...")
    
    try:
        # Connect to MongoDB
        await mongodb_client.connect()
        logger.info("✓ MongoDB connected")
        
        # Connect to Pinecone
        await pinecone_client.connect()
        logger.info("✓ Pinecone connected")
        
        logger.info("🚀 System ready!")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await mongodb_client.disconnect()
    await pinecone_client.disconnect()
    logger.info("✓ Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="LLM KPI Monitoring System",
    description="GenAI-powered API monitoring with LangGraph orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Register routers
app.include_router(logs_router)
app.include_router(kpis_router)
app.include_router(anomalies_router)
app.include_router(websocket_router)

# Mount static files for assets
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# Dashboard route - render HTML template on root
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the live monitoring dashboard."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        services={
            "mongodb": "connected",
            "pinecone": "connected",
            "llm": "groq-llama-3.3-70b"
        }
    )


# Database statistics endpoint
@app.get("/stats/databases")
async def database_stats():
    """Get MongoDB and Pinecone usage statistics."""
    try:
        # MongoDB stats
        mongo_stats = {
            "status": "connected",
            "database": settings.db_name,
            "collections": {}
        }
        
        # Get collection counts
        try:
            api_logs_count = await mongodb_client.db.api_logs.count_documents({})
            anomalies_count = await mongodb_client.db.anomalies.count_documents({})
            kpis_count = await mongodb_client.db.kpis.count_documents({})
            
            mongo_stats["collections"] = {
                "api_logs": api_logs_count,
                "anomalies": anomalies_count,
                "kpis": kpis_count,
                "total_documents": api_logs_count + anomalies_count + kpis_count
            }
        except Exception as e:
            logger.error(f"Failed to get MongoDB stats: {e}")
            mongo_stats["error"] = str(e)
        
        # Pinecone stats
        pinecone_stats = {
            "status": "connected",
            "index_name": settings.pinecone_index_name,
            "dimension": 384,
            "metric": "cosine"
        }
        
        try:
            index_stats = await pinecone_client.get_index_stats()
            pinecone_stats.update(index_stats)
        except Exception as e:
            logger.error(f"Failed to get Pinecone stats: {e}")
            pinecone_stats["error"] = str(e)
        
        return {
            "success": True,
            "mongodb": mongo_stats,
            "pinecone": pinecone_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Sample data endpoint for testing
@app.get("/stats/sample-data")
async def get_sample_data():
    """Get sample data from MongoDB to verify storage."""
    try:
        # Get latest logs
        latest_logs = await mongodb_client.get_recent_logs(limit=5)
        
        # Get latest anomalies
        from datetime import datetime, timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        latest_anomalies = await mongodb_client.get_anomalies(
            limit=5,
            start_time=start_time,
            end_time=end_time
        )
        
        # Convert ObjectId to string
        for log in latest_logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
            if "timestamp" in log and hasattr(log["timestamp"], "isoformat"):
                log["timestamp"] = log["timestamp"].isoformat()
        
        for anomaly in latest_anomalies:
            if "_id" in anomaly:
                anomaly["_id"] = str(anomaly["_id"])
            if "timestamp" in anomaly and hasattr(anomaly["timestamp"], "isoformat"):
                anomaly["timestamp"] = anomaly["timestamp"].isoformat()
        
        return {
            "success": True,
            "latest_logs": latest_logs,
            "latest_anomalies": latest_anomalies,
            "logs_count": len(latest_logs),
            "anomalies_count": len(latest_anomalies)
        }
        
    except Exception as e:
        logger.error(f"Failed to get sample data: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

