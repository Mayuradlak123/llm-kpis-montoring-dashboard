"""Routes package."""
from .logs import router as logs_router
from .kpis import router as kpis_router
from .anomalies import router as anomalies_router
from .websocket import router as websocket_router

__all__ = ["logs_router", "kpis_router", "anomalies_router", "websocket_router"]
