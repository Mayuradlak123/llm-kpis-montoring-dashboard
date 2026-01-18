"""
MongoDB async client for API log and KPI storage.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime

from config.logger import logger

from utils.config import settings


class MongoDBClient:
    """Async MongoDB client for log and KPI storage."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """Establish MongoDB connection."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.db = self.client[settings.mongodb_database]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {settings.mongodb_database}")
            
            # Create indexes for performance
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self):
        """Create indexes for efficient queries."""
        try:
            # API logs collection indexes
            await self.db.api_logs.create_index("timestamp")
            await self.db.api_logs.create_index("endpoint")
            await self.db.api_logs.create_index("is_anomaly")
            await self.db.api_logs.create_index([("timestamp", -1), ("endpoint", 1)])
            
            # KPIs collection indexes
            await self.db.kpis.create_index("created_at")
            await self.db.kpis.create_index("aggregation_type")
            
            # Anomalies collection indexes
            await self.db.anomalies.create_index("timestamp")
            await self.db.anomalies.create_index("anomaly_severity")
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    # API Logs Operations
    
    async def insert_log(self, log_data: Dict[str, Any]) -> str:
        """Insert a new API log document."""
        result = await self.db.api_logs.insert_one(log_data)
        return str(result.inserted_id)
    
    async def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a log by its ID."""
        from bson import ObjectId
        return await self.db.api_logs.find_one({"_id": ObjectId(log_id)})
    
    async def get_recent_logs(
        self,
        limit: int = 100,
        endpoint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent logs with optional endpoint filter."""
        query = {}
        if endpoint:
            query["endpoint"] = endpoint
        
        cursor = self.db.api_logs.find(query).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_logs_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime,
        endpoint: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get logs within a time range."""
        query = {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }
        if endpoint:
            query["endpoint"] = endpoint
        
        cursor = self.db.api_logs.find(query).sort("timestamp", -1)
        return await cursor.to_list(length=None)
    
    # KPI Operations
    
    async def insert_kpi(self, kpi_data: Dict[str, Any]) -> str:
        """Insert aggregated KPI document."""
        result = await self.db.kpis.insert_one(kpi_data)
        return str(result.inserted_id)
    
    async def get_latest_kpi(
        self,
        aggregation_type: str = "hourly"
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent KPI document."""
        return await self.db.kpis.find_one(
            {"aggregation_type": aggregation_type},
            sort=[("created_at", -1)]
        )
    
    # Anomaly Operations
    
    async def insert_anomaly(self, anomaly_data: Dict[str, Any]) -> str:
        """Insert anomaly record."""
        result = await self.db.anomalies.insert_one(anomaly_data)
        return str(result.inserted_id)
    
    async def get_anomalies(
        self,
        severity: Optional[str] = None,
        limit: int = 50,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get anomalies with optional filters."""
        query = {}
        
        if severity:
            query["anomaly_severity"] = severity
        
        if start_time and end_time:
            query["timestamp"] = {
                "$gte": start_time,
                "$lte": end_time
            }
        
        cursor = self.db.anomalies.find(query).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_anomaly_count(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """Count anomalies in time range."""
        query = {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time
            }
        }
        return await self.db.anomalies.count_documents(query)


# Global MongoDB client instance
mongodb_client = MongoDBClient()
