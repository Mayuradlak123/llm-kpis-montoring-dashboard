"""
LLM prompt templates for log analysis.
Enforces no hallucination, concise responses, and KPI awareness.
"""

SYSTEM_PROMPT = """You are an expert API monitoring system analyzer. Your role is to analyze API logs and provide concise, accurate insights.

CRITICAL RULES:
1. NO HALLUCINATION - Only analyze the data provided
2. BE CONCISE - Keep responses brief and actionable
3. KPI AWARENESS - Focus on latency, errors, and performance patterns
4. NO SPECULATION - If data is insufficient, state it clearly

Your analysis should identify:
- Performance issues (high latency, timeouts)
- Error patterns (status codes, error types)
- Anomalies (unusual behavior, spikes)
- Root cause indicators (when evident from data)

Format your response as a brief summary followed by specific findings."""

LOG_ANALYSIS_PROMPT = """Analyze this API log entry:

Endpoint: {endpoint}
Method: {method}
Status Code: {status_code}
Latency: {latency}ms
Error: {error}
Timestamp: {timestamp}

Provide a concise analysis covering:
1. Overall health assessment (1-2 sentences)
2. Any anomalies or concerns
3. Recommended action (if any)

Keep your response under 100 words."""

ANOMALY_DETECTION_PROMPT = """Given these API metrics:

Current Log:
- Endpoint: {endpoint}
- Latency: {latency}ms
- Status: {status_code}

Historical Context:
- Average Latency: {avg_latency}ms
- P95 Latency: {p95_latency}ms
- Error Rate: {error_rate}%

Is this log anomalous? Respond with:
1. YES/NO
2. Severity (LOW/MEDIUM/HIGH/CRITICAL) if anomalous
3. Brief reason (1 sentence)

Format: ANSWER | SEVERITY | REASON"""

BATCH_SUMMARY_PROMPT = """Summarize the health of this API over the last hour:

Total Requests: {total_requests}
Success Rate: {success_rate}%
Average Latency: {avg_latency}ms
P95 Latency: {p95_latency}ms
Error Count: {error_count}
Top Errors: {top_errors}

Provide:
1. Overall health status (HEALTHY/DEGRADED/CRITICAL)
2. Key concerns (if any)
3. Trend assessment

Keep response under 75 words."""


def get_log_analysis_prompt(
    endpoint: str,
    method: str,
    status_code: int,
    latency: float,
    error: str | None,
    timestamp: str
) -> str:
    """Generate log analysis prompt with provided data."""
    return LOG_ANALYSIS_PROMPT.format(
        endpoint=endpoint,
        method=method,
        status_code=status_code,
        latency=latency,
        error=error or "None",
        timestamp=timestamp
    )


def get_anomaly_detection_prompt(
    endpoint: str,
    latency: float,
    status_code: int,
    avg_latency: float,
    p95_latency: float,
    error_rate: float
) -> str:
    """Generate anomaly detection prompt with metrics."""
    return ANOMALY_DETECTION_PROMPT.format(
        endpoint=endpoint,
        latency=latency,
        status_code=status_code,
        avg_latency=avg_latency,
        p95_latency=p95_latency,
        error_rate=error_rate
    )


def get_batch_summary_prompt(
    total_requests: int,
    success_rate: float,
    avg_latency: float,
    p95_latency: float,
    error_count: int,
    top_errors: str
) -> str:
    """Generate batch summary prompt with aggregated metrics."""
    return BATCH_SUMMARY_PROMPT.format(
        total_requests=total_requests,
        success_rate=success_rate,
        avg_latency=avg_latency,
        p95_latency=p95_latency,
        error_count=error_count,
        top_errors=top_errors
    )
