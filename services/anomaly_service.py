"""
Anomaly detection service combining statistical and LLM-based methods.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from config.logger import logger

from database.mongodb import mongodb_client
from services.llm_service import llm_service
from services.kpi_service import kpi_service
from models.kpi_models import AnomalyScore
from models.response_models import AnomalyResponse
from utils.metrics import (
    detect_anomaly_zscore,
    detect_anomaly_iqr,
    get_severity_from_status,
    get_severity_from_latency,
    time_range_to_datetime
)


class AnomalyService:
    """Service for detecting anomalies in API logs."""
    
    async def detect_anomaly(
        self,
        log_data: Dict[str, Any],
        use_llm: bool = True
    ) -> AnomalyScore:
        """
        Detect if a log entry is anomalous.
        
        Combines statistical methods with LLM-based analysis.
        
        Args:
            log_data: Log entry data
            use_llm: Whether to use LLM for additional analysis
        
        Returns:
            AnomalyScore with detection results
        """
        endpoint = log_data.get('endpoint', 'unknown')
        latency = log_data.get('latency', 0)
        status_code = log_data.get('status_code', 200)
        
        # Get historical context for this endpoint
        kpi_metrics = await kpi_service.get_aggregated_kpis(
            time_range="1h",
            endpoint=endpoint
        )
        
        # Statistical anomaly detection
        is_anomaly_stat = False
        z_score = 0.0
        detected_patterns = []
        
        # Check latency anomaly
        if kpi_metrics.total_requests > 10:  # Need sufficient data
            # Z-score method
            is_latency_anomaly, z_score = detect_anomaly_zscore(
                value=latency,
                mean=kpi_metrics.avg_latency,
                std=max(kpi_metrics.p95_latency - kpi_metrics.avg_latency, 1.0),
                threshold=2.5
            )
            
            if is_latency_anomaly:
                is_anomaly_stat = True
                detected_patterns.append(f"Latency {latency:.0f}ms exceeds normal range")
        
        # Check status code
        if status_code >= 500:
            is_anomaly_stat = True
            detected_patterns.append(f"Server error: {status_code}")
        elif status_code >= 400:
            # Client errors are less severe but still notable
            detected_patterns.append(f"Client error: {status_code}")
        
        # Determine initial severity from status and latency
        status_severity = get_severity_from_status(status_code)
        latency_severity = get_severity_from_latency(
            latency,
            kpi_metrics.p95_latency,
            kpi_metrics.p99_latency
        )
        
        # Take the higher severity
        severity_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        severity = max(
            [status_severity, latency_severity],
            key=lambda s: severity_map.get(s, 0)
        )
        
        # LLM-based anomaly detection (if enabled and anomaly detected)
        llm_reason = None
        if use_llm and (is_anomaly_stat or status_code >= 400):
            is_llm_anomaly, llm_severity, llm_reason = await llm_service.detect_anomaly_with_llm(
                endpoint=endpoint,
                latency=latency,
                status_code=status_code,
                avg_latency=kpi_metrics.avg_latency,
                p95_latency=kpi_metrics.p95_latency,
                error_rate=kpi_metrics.error_rate
            )
            
            # LLM can override statistical detection
            if is_llm_anomaly and llm_severity:
                is_anomaly_stat = True
                severity = llm_severity
                detected_patterns.append(f"LLM detected: {llm_reason}")
        
        # Calculate confidence
        confidence = 0.5
        if is_anomaly_stat:
            confidence = min(0.95, 0.6 + (abs(z_score) * 0.1))
        
        # Build reason
        reason = llm_reason if llm_reason else " | ".join(detected_patterns) if detected_patterns else "Within normal range"
        
        return AnomalyScore(
            is_anomaly=is_anomaly_stat,
            severity=severity if is_anomaly_stat else None,
            confidence=confidence,
            reason=reason,
            detected_patterns=detected_patterns if detected_patterns else None,
            z_score=z_score if z_score != 0.0 else None
        )
    
    async def get_anomalies(
        self,
        severity: Optional[str] = None,
        time_range: str = "1h",
        limit: int = 50
    ) -> List[AnomalyResponse]:
        """
        Retrieve anomalies from database.
        
        Args:
            severity: Filter by severity level
            time_range: Time range to query
            limit: Maximum number of results
        
        Returns:
            List of anomaly responses
        """
        start_time, end_time = time_range_to_datetime(time_range)
        
        # Get anomalies from MongoDB
        anomaly_docs = await mongodb_client.get_anomalies(
            severity=severity,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        # Convert to response models
        anomalies = []
        for doc in anomaly_docs:
            anomaly_score = AnomalyScore(
                is_anomaly=doc.get('is_anomaly', True),
                severity=doc.get('anomaly_severity'),
                confidence=doc.get('anomaly_score', 0.0),
                reason=doc.get('anomaly_reason', 'Unknown'),
                detected_patterns=None,
                z_score=None
            )
            
            anomaly = AnomalyResponse(
                log_id=str(doc.get('_id')),
                endpoint=doc.get('endpoint', 'unknown'),
                method=doc.get('method', 'unknown'),
                status_code=doc.get('status_code', 0),
                latency=doc.get('latency', 0.0),
                timestamp=doc.get('timestamp', datetime.utcnow()),
                anomaly_score=anomaly_score,
                llm_analysis=doc.get('llm_analysis')
            )
            anomalies.append(anomaly)
        
        return anomalies


# Global anomaly service instance
anomaly_service = AnomalyService()
