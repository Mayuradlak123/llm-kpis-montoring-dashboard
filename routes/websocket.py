"""
WebSocket route for real-time KPI streaming.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Any
import asyncio
import json
from datetime import datetime

from config.logger import logger

from services.kpi_service import kpi_service
from database.mongodb import mongodb_client

router = APIRouter(tags=["websocket"])

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


@router.websocket("/live-kpis")
async def websocket_live_kpis(websocket: WebSocket):
    """
    WebSocket endpoint for real-time KPI updates.
    
    Streams:
    - New log entries
    - Updated KPI metrics
    - Anomaly alerts
    """
    await websocket.accept()
    active_connections.add(websocket)
    
    logger.info(f"WebSocket connected. Total connections: {len(active_connections)}")
    
    try:
        # Send initial KPIs
        initial_kpis = await kpi_service.get_aggregated_kpis(time_range="1h")
        await websocket.send_json({
            "type": "initial_kpis",
            "data": _make_serializable(initial_kpis.model_dump()),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Start streaming updates
        while True:
            try:
                # Wait for client messages (heartbeat)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                # Handle client requests
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "get_kpis":
                    kpis = await kpi_service.get_aggregated_kpis(time_range="1h")
                    await websocket.send_json({
                        "type": "kpi_update",
                        "data": _make_serializable(kpis.model_dump()),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif data == "get_recent_logs":
                    logs = await mongodb_client.get_recent_logs(limit=10)
                    # Use helper for consistent serialization
                    serializable_logs = _make_serializable(logs)
                    
                    await websocket.send_json({
                        "type": "recent_logs",
                        "data": serializable_logs,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except asyncio.TimeoutError:
                # Send periodic updates even without client messages
                try:
                    kpis = await kpi_service.get_aggregated_kpis(time_range="1h")
                    await websocket.send_json({
                        "type": "kpi_update",
                        "data": _make_serializable(kpis.model_dump()),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Failed to send periodic update: {e}")
                    break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.discard(websocket)
        logger.info(f"WebSocket removed. Total connections: {len(active_connections)}")


from bson import ObjectId

def _make_serializable(data: Any) -> Any:
    """Recursively convert datetime and ObjectId objects to JSON serializable formats."""
    if isinstance(data, dict):
        return {k: _make_serializable(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_make_serializable(item) for item in data]
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, ObjectId):
        return str(data)
    return data


async def broadcast_new_log(log_data: dict):
    """Broadcast new log to all connected clients."""
    if not active_connections:
        return
    
    # Ensure data is JSON serializable
    serializable_data = _make_serializable(log_data)
    
    message = {
        "type": "new_log",
        "data": serializable_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to all connections
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to broadcast to connection: {e}")
            disconnected.add(connection)
    
    # Remove disconnected clients
    active_connections.difference_update(disconnected)


async def broadcast_anomaly(anomaly_data: dict):
    """Broadcast anomaly alert to all connected clients."""
    if not active_connections:
        return
    
    # Ensure data is JSON serializable
    serializable_data = _make_serializable(anomaly_data)
    
    message = {
        "type": "anomaly_alert",
        "data": serializable_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    disconnected = set()
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Failed to broadcast anomaly: {e}")
            disconnected.add(connection)
    
    active_connections.difference_update(disconnected)
