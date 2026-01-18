"""
KPI service for aggregating and calculating metrics.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from config.logger import logger

from database.mongodb import mongodb_client
from models.kpi_models import KPIMetrics, LLMMetrics
from utils.metrics import (
    calculate_mean,
    calculate_percentile,
    calculate_error_rate,
    calculate_success_rate,
    time_range_to_datetime
)


class KPIService:
    """Service for KPI aggregation and calculation."""
    
    async def get_aggregated_kpis(
        self,
        time_range: str = "1h",
        endpoint: Optional[str] = None
    ) -> KPIMetrics:
        """
        Calculate aggregated KPIs for a time range.
        
        Args:
            time_range: Time range string ("1h", "24h", "7d", "30d")
            endpoint: Optional endpoint filter
        
        Returns:
            KPIMetrics object with calculated metrics
        """
        # Get time range
        start_time, end_time = time_range_to_datetime(time_range)
        
        # Fetch logs from MongoDB
        logs = await mongodb_client.get_logs_in_timerange(
            start_time=start_time,
            end_time=end_time,
            endpoint=endpoint
        )
        
        if not logs:
            # Return zero metrics if no data
            return KPIMetrics(
                total_requests=0,
                success_count=0,
                error_count=0,
                success_rate=0.0,
                error_rate=0.0,
                avg_latency=0.0,
                p50_latency=0.0,
                p95_latency=0.0,
                p99_latency=0.0,
                max_latency=0.0,
                time_range=time_range,
                start_time=start_time,
                end_time=end_time,
                endpoint=endpoint
            )
        
        # Calculate metrics
        total_requests = len(logs)
        success_count = sum(1 for log in logs if 200 <= log.get('status_code', 0) < 300)
        error_count = total_requests - success_count
        
        latencies = [log.get('latency', 0) for log in logs]
        
        kpi_metrics = KPIMetrics(
            total_requests=total_requests,
            success_count=success_count,
            error_count=error_count,
            success_rate=calculate_success_rate(total_requests, success_count),
            error_rate=calculate_error_rate(total_requests, error_count),
            avg_latency=calculate_mean(latencies),
            p50_latency=calculate_percentile(latencies, 50),
            p95_latency=calculate_percentile(latencies, 95),
            p99_latency=calculate_percentile(latencies, 99),
            max_latency=max(latencies) if latencies else 0.0,
            time_range=time_range,
            start_time=start_time,
            end_time=end_time,
            endpoint=endpoint
        )
        
        logger.info(f"Calculated KPIs for {time_range}: {total_requests} requests")
        
        return kpi_metrics
    
    async def get_llm_metrics(
        self,
        time_range: str = "1h"
    ) -> LLMMetrics:
        """Calculate LLM usage metrics."""
        start_time, end_time = time_range_to_datetime(time_range)
        
        logs = await mongodb_client.get_logs_in_timerange(
            start_time=start_time,
            end_time=end_time
        )
        
        if not logs:
            return LLMMetrics(
                total_llm_calls=0,
                total_input_tokens=0,
                total_output_tokens=0,
                total_cost=0.0,
                avg_llm_latency=0.0,
                time_range=time_range,
                start_time=start_time,
                end_time=end_time
            )
        
        # Aggregate LLM metrics
        total_llm_calls = sum(1 for log in logs if log.get('llm_tokens_input', 0) > 0)
        total_input_tokens = sum(log.get('llm_tokens_input', 0) for log in logs)
        total_output_tokens = sum(log.get('llm_tokens_output', 0) for log in logs)
        total_cost = sum(log.get('llm_cost', 0.0) for log in logs)
        
        llm_latencies = [log.get('llm_latency', 0) for log in logs if log.get('llm_latency', 0) > 0]
        avg_llm_latency = calculate_mean(llm_latencies) if llm_latencies else 0.0
        
        return LLMMetrics(
            total_llm_calls=total_llm_calls,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            avg_llm_latency=avg_llm_latency,
            time_range=time_range,
            start_time=start_time,
            end_time=end_time
        )
    
    async def get_endpoint_breakdown(
        self,
        time_range: str = "1h"
    ) -> Dict[str, KPIMetrics]:
        """Get KPI metrics broken down by endpoint."""
        start_time, end_time = time_range_to_datetime(time_range)
        
        logs = await mongodb_client.get_logs_in_timerange(
            start_time=start_time,
            end_time=end_time
        )
        
        # Group by endpoint
        endpoint_logs: Dict[str, List[Dict[str, Any]]] = {}
        for log in logs:
            endpoint = log.get('endpoint', 'unknown')
            if endpoint not in endpoint_logs:
                endpoint_logs[endpoint] = []
            endpoint_logs[endpoint].append(log)
        
        # Calculate metrics for each endpoint
        endpoint_metrics = {}
        for endpoint, logs_list in endpoint_logs.items():
            metrics = await self.get_aggregated_kpis(
                time_range=time_range,
                endpoint=endpoint
            )
            endpoint_metrics[endpoint] = metrics
        
        return endpoint_metrics


# Global KPI service instance
kpi_service = KPIService()
