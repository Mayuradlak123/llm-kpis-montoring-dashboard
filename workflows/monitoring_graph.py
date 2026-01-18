"""
LangGraph workflow for API log monitoring and analysis.

This workflow orchestrates the complete log processing pipeline:
1. Input Validation
2. KPI Extraction
3. LLM Analysis
4. Anomaly Detection
5. MongoDB Persistence
6. Embedding Generation
7. Pinecone Storage
8. Response Formatting
"""
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime

from config.logger import logger
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

from services.llm_service import llm_service
from services.embedding_service import embedding_service
from services.anomaly_service import anomaly_service
from database.mongodb import mongodb_client
from database.pinecone_client import pinecone_client
from models.log_models import APILogRequest


# Define workflow state
class MonitoringState(TypedDict):
    """State maintained throughout the workflow."""
    
    # Input data
    log_request: Dict[str, Any]
    
    # Processing flags
    is_valid: bool
    validation_error: Optional[str]
    
    # Extracted KPIs
    endpoint: str
    method: str
    status_code: int
    latency: float
    error: Optional[str]
    timestamp: datetime
    
    # LLM analysis results
    llm_analysis: Optional[str]
    llm_tokens_input: int
    llm_tokens_output: int
    llm_latency: float
    llm_cost: float
    
    # Anomaly detection
    is_anomaly: bool
    anomaly_score: float
    anomaly_severity: Optional[str]
    anomaly_reason: Optional[str]
    
    # Database IDs
    mongodb_id: Optional[str]
    embedding_id: Optional[str]
    
    # Embedding
    embedding_vector: Optional[List[float]]
    
    # Final response
    response: Dict[str, Any]
    processing_start_time: float


# Node 1: Input Validation
async def validate_input(state: MonitoringState) -> MonitoringState:
    """Validate incoming log data."""
    logger.info("Node 1: Validating input")
    
    try:
        # Validate using Pydantic model
        log_data = state["log_request"]
        validated_log = APILogRequest(**log_data)
        
        state["is_valid"] = True
        state["validation_error"] = None
        
        logger.debug("Input validation passed")
        
    except Exception as e:
        state["is_valid"] = False
        state["validation_error"] = str(e)
        logger.error(f"Input validation failed: {e}")
    
    return state


# Node 2: KPI Extraction
async def extract_kpis(state: MonitoringState) -> MonitoringState:
    """Extract KPIs from validated log."""
    logger.info("Node 2: Extracting KPIs")
    
    log_data = state["log_request"]
    
    state["endpoint"] = log_data.get("endpoint", "unknown")
    state["method"] = log_data.get("method", "GET")
    state["status_code"] = log_data.get("status_code", 0)
    state["latency"] = log_data.get("latency", 0.0)
    state["error"] = log_data.get("error")
    state["timestamp"] = datetime.utcnow()
    
    logger.debug(f"Extracted KPIs: {state['endpoint']} - {state['status_code']} - {state['latency']}ms")
    
    return state


# Node 3: LLM Analysis
async def analyze_with_llm(state: MonitoringState) -> MonitoringState:
    """Analyze log using Groq LLM."""
    logger.info("Node 3: Analyzing with LLM")
    
    try:
        analysis, input_tokens, output_tokens, llm_latency, cost = await llm_service.analyze_log(
            endpoint=state["endpoint"],
            method=state["method"],
            status_code=state["status_code"],
            latency=state["latency"],
            error=state["error"],
            timestamp=state["timestamp"].isoformat()
        )
        
        state["llm_analysis"] = analysis
        state["llm_tokens_input"] = input_tokens
        state["llm_tokens_output"] = output_tokens
        state["llm_latency"] = llm_latency
        state["llm_cost"] = cost
        
        logger.debug(f"LLM analysis completed: {len(analysis)} chars, {input_tokens + output_tokens} tokens")
        
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        state["llm_analysis"] = "Analysis unavailable"
        state["llm_tokens_input"] = 0
        state["llm_tokens_output"] = 0
        state["llm_latency"] = 0.0
        state["llm_cost"] = 0.0
    
    return state


# Node 4: Anomaly Detection
async def detect_anomaly(state: MonitoringState) -> MonitoringState:
    """Detect anomalies using statistical and LLM methods."""
    logger.info("Node 4: Detecting anomalies")
    
    try:
        # Prepare log data for anomaly detection
        log_data = {
            "endpoint": state["endpoint"],
            "method": state["method"],
            "status_code": state["status_code"],
            "latency": state["latency"],
            "error": state["error"]
        }
        
        anomaly_score = await anomaly_service.detect_anomaly(log_data, use_llm=True)
        
        state["is_anomaly"] = anomaly_score.is_anomaly
        state["anomaly_score"] = anomaly_score.confidence
        state["anomaly_severity"] = anomaly_score.severity
        state["anomaly_reason"] = anomaly_score.reason
        
        logger.debug(f"Anomaly detection: {state['is_anomaly']} (severity: {state['anomaly_severity']})")
        
    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        state["is_anomaly"] = False
        state["anomaly_score"] = 0.0
        state["anomaly_severity"] = None
        state["anomaly_reason"] = "Detection failed"
    
    return state


# Node 5: Persist to MongoDB
async def persist_to_mongodb(state: MonitoringState) -> MonitoringState:
    """Store log and analysis results in MongoDB."""
    logger.info("Node 5: Persisting to MongoDB")
    
    try:
        # Prepare document
        log_document = {
            "endpoint": state["endpoint"],
            "method": state["method"],
            "status_code": state["status_code"],
            "latency": state["latency"],
            "error": state["error"],
            "timestamp": state["timestamp"],
            "llm_analysis": state["llm_analysis"],
            "is_anomaly": state["is_anomaly"],
            "anomaly_score": state["anomaly_score"],
            "anomaly_severity": state["anomaly_severity"],
            "anomaly_reason": state["anomaly_reason"],
            "llm_tokens_input": state["llm_tokens_input"],
            "llm_tokens_output": state["llm_tokens_output"],
            "llm_cost": state["llm_cost"],
            "llm_latency": state["llm_latency"]
        }
        
        # Add optional fields
        if state["log_request"].get("user_id"):
            log_document["user_id"] = state["log_request"]["user_id"]
        if state["log_request"].get("trace_id"):
            log_document["trace_id"] = state["log_request"]["trace_id"]
        
        # Insert into MongoDB
        log_id = await mongodb_client.insert_log(log_document)
        state["mongodb_id"] = log_id
        
        # If anomaly, also insert into anomalies collection
        if state["is_anomaly"]:
            await mongodb_client.insert_anomaly(log_document)
        
        logger.debug(f"Persisted to MongoDB: {log_id}")
        
    except Exception as e:
        logger.error(f"MongoDB persistence failed: {e}")
        state["mongodb_id"] = None
    
    return state


# Node 6: Generate Embedding
async def generate_embedding(state: MonitoringState) -> MonitoringState:
    """Generate vector embedding for semantic search."""
    logger.info("Node 6: Generating embedding")
    
    try:
        # Prepare log data for embedding
        log_data = {
            "endpoint": state["endpoint"],
            "method": state["method"],
            "status_code": state["status_code"],
            "latency": state["latency"],
            "error": state["error"],
            "llm_analysis": state["llm_analysis"]
        }
        
        embedding_vector = await embedding_service.generate_embedding(log_data)
        state["embedding_vector"] = embedding_vector
        
        # Generate unique ID
        state["embedding_id"] = pinecone_client.generate_embedding_id({
            "endpoint": state["endpoint"],
            "timestamp": state["timestamp"],
            "trace_id": state["log_request"].get("trace_id", "")
        })
        
        logger.debug(f"Generated embedding: {len(embedding_vector)} dimensions")
        
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        state["embedding_vector"] = None
        state["embedding_id"] = None
    
    return state


# Node 7: Store in Pinecone
async def store_in_pinecone(state: MonitoringState) -> MonitoringState:
    """Store embedding in Pinecone for semantic search."""
    logger.info("Node 7: Storing in Pinecone")
    
    if state["embedding_vector"] and state["embedding_id"]:
        try:
            # Prepare metadata
            metadata = {
                "endpoint": state["endpoint"],
                "method": state["method"],
                "status_code": state["status_code"],
                "latency": state["latency"],
                "timestamp": state["timestamp"],
                "is_anomaly": state["is_anomaly"],
                "anomaly_severity": state["anomaly_severity"] or "NONE",
                "mongodb_id": state["mongodb_id"] or ""
            }
            
            # Upsert to Pinecone
            success = await pinecone_client.upsert_embedding(
                embedding_id=state["embedding_id"],
                embedding_vector=state["embedding_vector"],
                metadata=metadata
            )
            
            if success:
                logger.debug(f"Stored in Pinecone: {state['embedding_id']}")
            else:
                logger.warning("Pinecone storage failed")
                
        except Exception as e:
            logger.error(f"Pinecone storage error: {e}")
    else:
        logger.warning("Skipping Pinecone storage (no embedding)")
    
    return state


# Node 8: Format Response
async def format_response(state: MonitoringState) -> MonitoringState:
    """Format final API response."""
    logger.info("Node 8: Formatting response")
    
    import time
    processing_time = (time.time() - state["processing_start_time"]) * 1000  # ms
    
    state["response"] = {
        "success": True,
        "log_id": state["mongodb_id"],
        "analysis_summary": state["llm_analysis"],
        "is_anomaly": state["is_anomaly"],
        "anomaly_severity": state["anomaly_severity"],
        "processing_time_ms": processing_time
    }
    
    logger.info(f"Workflow completed in {processing_time:.2f}ms")
    
    return state


# Conditional routing function
def should_continue(state: MonitoringState) -> str:
    """Determine if workflow should continue or end."""
    if not state.get("is_valid", False):
        return "end"
    return "continue"


# Build the LangGraph workflow
def create_monitoring_graph() -> StateGraph:
    """Create and compile the monitoring workflow graph."""
    
    workflow = StateGraph(MonitoringState)
    
    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("extract_kpis", extract_kpis)
    workflow.add_node("analyze_with_llm", analyze_with_llm)
    workflow.add_node("detect_anomaly", detect_anomaly)
    workflow.add_node("persist_to_mongodb", persist_to_mongodb)
    workflow.add_node("generate_embedding", generate_embedding)
    workflow.add_node("store_in_pinecone", store_in_pinecone)
    workflow.add_node("format_response", format_response)
    
    # Set entry point
    workflow.set_entry_point("validate_input")
    
    # Add edges (sequential flow)
    workflow.add_edge("validate_input", "extract_kpis")
    workflow.add_edge("extract_kpis", "analyze_with_llm")
    workflow.add_edge("analyze_with_llm", "detect_anomaly")
    workflow.add_edge("detect_anomaly", "persist_to_mongodb")
    workflow.add_edge("persist_to_mongodb", "generate_embedding")
    workflow.add_edge("generate_embedding", "store_in_pinecone")
    workflow.add_edge("store_in_pinecone", "format_response")
    workflow.add_edge("format_response", END)
    
    # Compile the graph
    return workflow.compile()


# Global compiled graph instance
monitoring_graph = create_monitoring_graph()


async def process_log(log_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a log through the complete monitoring workflow.
    
    Args:
        log_request: API log data
    
    Returns:
        Processing result with analysis and anomaly detection
    """
    import time
    
    # Initialize state
    initial_state: MonitoringState = {
        "log_request": log_request,
        "is_valid": False,
        "validation_error": None,
        "endpoint": "",
        "method": "",
        "status_code": 0,
        "latency": 0.0,
        "error": None,
        "timestamp": datetime.utcnow(),
        "llm_analysis": None,
        "llm_tokens_input": 0,
        "llm_tokens_output": 0,
        "llm_latency": 0.0,
        "llm_cost": 0.0,
        "is_anomaly": False,
        "anomaly_score": 0.0,
        "anomaly_severity": None,
        "anomaly_reason": None,
        "mongodb_id": None,
        "embedding_id": None,
        "embedding_vector": None,
        "response": {},
        "processing_start_time": time.time()
    }
    
    # Execute workflow
    try:
        final_state = await monitoring_graph.ainvoke(initial_state)
        return final_state["response"]
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "processing_time_ms": (time.time() - initial_state["processing_start_time"]) * 1000
        }
