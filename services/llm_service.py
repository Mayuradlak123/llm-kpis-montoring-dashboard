"""
Groq LLM service for log analysis and anomaly detection.
"""
from groq import AsyncGroq
from typing import Optional, Tuple
import time

from config.logger import logger

from utils.config import settings
from utils.prompts import SYSTEM_PROMPT, get_log_analysis_prompt, get_anomaly_detection_prompt
from utils.metrics import estimate_llm_cost


class LLMService:
    """Service for interacting with Groq LLM."""
    
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.groq_api_key)
        self.model = settings.groq_model
    
    async def analyze_log(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        latency: float,
        error: Optional[str],
        timestamp: str
    ) -> Tuple[str, int, int, float, float]:
        """
        Analyze a single log entry using LLM.
        
        Returns:
            Tuple of (analysis, input_tokens, output_tokens, llm_latency, cost)
        """
        start_time = time.time()
        
        try:
            # Generate prompt
            user_prompt = get_log_analysis_prompt(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                latency=latency,
                error=error,
                timestamp=timestamp
            )
            
            # Call Groq LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent analysis
                max_tokens=200
            )
            
            # Extract response
            analysis = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Calculate metrics
            llm_latency = (time.time() - start_time) * 1000  # Convert to ms
            cost = estimate_llm_cost(
                input_tokens,
                output_tokens,
                settings.groq_cost_per_1m_input_tokens,
                settings.groq_cost_per_1m_output_tokens
            )
            
            logger.debug(f"LLM analysis completed in {llm_latency:.2f}ms")
            
            return analysis, input_tokens, output_tokens, llm_latency, cost
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            # Return fallback response
            return (
                "Analysis unavailable due to LLM error",
                0,
                0,
                (time.time() - start_time) * 1000,
                0.0
            )
    
    async def detect_anomaly_with_llm(
        self,
        endpoint: str,
        latency: float,
        status_code: int,
        avg_latency: float,
        p95_latency: float,
        error_rate: float
    ) -> Tuple[bool, Optional[str], str]:
        """
        Use LLM to detect anomalies with context.
        
        Returns:
            Tuple of (is_anomaly, severity, reason)
        """
        try:
            # Generate prompt
            user_prompt = get_anomaly_detection_prompt(
                endpoint=endpoint,
                latency=latency,
                status_code=status_code,
                avg_latency=avg_latency,
                p95_latency=p95_latency,
                error_rate=error_rate
            )
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=100
            )
            
            # Parse response (format: ANSWER | SEVERITY | REASON)
            content = response.choices[0].message.content.strip()
            parts = [p.strip() for p in content.split("|")]
            
            if len(parts) >= 3:
                is_anomaly = parts[0].upper() == "YES"
                severity = parts[1] if is_anomaly else None
                reason = parts[2]
            else:
                # Fallback parsing
                is_anomaly = "YES" in content.upper()
                severity = "MEDIUM" if is_anomaly else None
                reason = content
            
            return is_anomaly, severity, reason
            
        except Exception as e:
            logger.error(f"LLM anomaly detection failed: {e}")
            return False, None, "LLM detection unavailable"
    
    async def generate_batch_summary(
        self,
        total_requests: int,
        success_rate: float,
        avg_latency: float,
        p95_latency: float,
        error_count: int,
        top_errors: str
    ) -> str:
        """Generate summary of API health over a time period."""
        try:
            from utils.prompts import get_batch_summary_prompt
            
            user_prompt = get_batch_summary_prompt(
                total_requests=total_requests,
                success_rate=success_rate,
                avg_latency=avg_latency,
                p95_latency=p95_latency,
                error_count=error_count,
                top_errors=top_errors
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Batch summary generation failed: {e}")
            return "Summary unavailable"


# Global LLM service instance
llm_service = LLMService()
