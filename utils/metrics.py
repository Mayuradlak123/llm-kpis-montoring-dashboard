"""
Metric calculation utilities for KPI analysis and anomaly detection.
"""
import numpy as np
from typing import List, Tuple
from datetime import datetime, timedelta


def calculate_percentile(values: List[float], percentile: int) -> float:
    """Calculate the specified percentile of a list of values."""
    if not values:
        return 0.0
    return float(np.percentile(values, percentile))


def calculate_mean(values: List[float]) -> float:
    """Calculate the mean of a list of values."""
    if not values:
        return 0.0
    return float(np.mean(values))


def calculate_std(values: List[float]) -> float:
    """Calculate the standard deviation of a list of values."""
    if not values:
        return 0.0
    return float(np.std(values))


def detect_anomaly_zscore(
    value: float,
    mean: float,
    std: float,
    threshold: float = 3.0
) -> Tuple[bool, float]:
    """
    Detect anomaly using z-score method.
    
    Returns:
        Tuple of (is_anomaly, z_score)
    """
    if std == 0:
        return False, 0.0
    
    z_score = abs((value - mean) / std)
    is_anomaly = z_score > threshold
    
    return is_anomaly, z_score


def detect_anomaly_iqr(
    value: float,
    values: List[float],
    multiplier: float = 1.5
) -> Tuple[bool, str]:
    """
    Detect anomaly using Interquartile Range (IQR) method.
    
    Returns:
        Tuple of (is_anomaly, reason)
    """
    if len(values) < 4:
        return False, "Insufficient data"
    
    q1 = calculate_percentile(values, 25)
    q3 = calculate_percentile(values, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - (multiplier * iqr)
    upper_bound = q3 + (multiplier * iqr)
    
    if value < lower_bound:
        return True, f"Value {value:.2f} below lower bound {lower_bound:.2f}"
    elif value > upper_bound:
        return True, f"Value {value:.2f} above upper bound {upper_bound:.2f}"
    
    return False, "Within normal range"


def calculate_error_rate(total_requests: int, error_count: int) -> float:
    """Calculate error rate as a percentage."""
    if total_requests == 0:
        return 0.0
    return (error_count / total_requests) * 100


def calculate_success_rate(total_requests: int, success_count: int) -> float:
    """Calculate success rate as a percentage."""
    if total_requests == 0:
        return 0.0
    return (success_count / total_requests) * 100


def estimate_llm_cost(
    input_tokens: int,
    output_tokens: int,
    cost_per_1m_input: float,
    cost_per_1m_output: float
) -> float:
    """
    Estimate LLM cost based on token usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        cost_per_1m_input: Cost per 1M input tokens in USD
        cost_per_1m_output: Cost per 1M output tokens in USD
    
    Returns:
        Estimated cost in USD
    """
    input_cost = (input_tokens / 1_000_000) * cost_per_1m_input
    output_cost = (output_tokens / 1_000_000) * cost_per_1m_output
    return input_cost + output_cost


def get_severity_from_status(status_code: int) -> str:
    """Determine severity level from HTTP status code."""
    if 200 <= status_code < 300:
        return "LOW"
    elif 300 <= status_code < 400:
        return "LOW"
    elif 400 <= status_code < 500:
        return "MEDIUM"
    elif status_code >= 500:
        return "HIGH"
    else:
        return "UNKNOWN"


def get_severity_from_latency(latency: float, p95: float, p99: float) -> str:
    """Determine severity level from latency metrics."""
    if latency < p95:
        return "LOW"
    elif latency < p99:
        return "MEDIUM"
    elif latency < p99 * 2:
        return "HIGH"
    else:
        return "CRITICAL"


def time_range_to_datetime(time_range: str) -> Tuple[datetime, datetime]:
    """
    Convert time range string to datetime range.
    
    Args:
        time_range: One of "1h", "24h", "7d", "30d"
    
    Returns:
        Tuple of (start_time, end_time)
    """
    end_time = datetime.utcnow()
    
    if time_range == "1h":
        start_time = end_time - timedelta(hours=1)
    elif time_range == "24h":
        start_time = end_time - timedelta(hours=24)
    elif time_range == "7d":
        start_time = end_time - timedelta(days=7)
    elif time_range == "30d":
        start_time = end_time - timedelta(days=30)
    else:
        # Default to 1 hour
        start_time = end_time - timedelta(hours=1)
    
    return start_time, end_time
