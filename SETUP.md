# LLM KPI Monitoring System - Complete Setup Guide

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [What This System Does](#what-this-system-does)
3. [Architecture & Technology Stack](#architecture--technology-stack)
4. [Prerequisites](#prerequisites)
5. [Installation Guide](#installation-guide)
6. [Configuration](#configuration)
7. [Project Structure Explained](#project-structure-explained)
8. [How It Works](#how-it-works)
9. [API Documentation](#api-documentation)
10. [Dashboard Usage](#dashboard-usage)
11. [Testing & Verification](#testing--verification)
12. [Troubleshooting](#troubleshooting)
13. [Advanced Usage](#advanced-usage)

---

## 🎯 Project Overview

**LLM KPI Monitoring System** is a production-ready, GenAI-powered API monitoring platform that intelligently analyzes API logs, detects anomalies, and provides real-time insights using Large Language Models (LLMs) and advanced machine learning techniques.

### Key Highlights

- 🤖 **AI-Powered Analysis**: Uses Groq's LLM (llama-3.3-70b-versatile) for intelligent log interpretation
- 🔄 **LangGraph Orchestration**: 8-node workflow for systematic log processing
- 📊 **Real-Time Dashboard**: Live KPI updates via WebSocket
- 🔍 **Semantic Search**: Vector embeddings for finding similar incidents
- 🚨 **Smart Anomaly Detection**: Combines statistical methods with LLM insights
- 💾 **Dual Storage**: MongoDB for structured data, Pinecone for vector search

---

## 🎬 What This System Does

### Primary Functions

1. **Log Ingestion & Analysis**
   - Receives API logs from your applications
   - Validates and structures the data
   - Analyzes each log using AI for insights

2. **Intelligent Anomaly Detection**
   - Detects unusual patterns (high latency, errors, spikes)
   - Uses both statistical methods (z-score, IQR) and LLM reasoning
   - Classifies severity: LOW, MEDIUM, HIGH, CRITICAL

3. **KPI Calculation & Tracking**
   - Monitors: latency (avg, P50, P95, P99), error rates, success rates
   - Tracks LLM usage: token consumption, costs
   - Aggregates metrics by time range and endpoint

4. **Semantic Search**
   - Converts logs to vector embeddings
   - Enables queries like "find similar outages" or "past incidents like this"
   - Stores in Pinecone for fast similarity search

5. **Real-Time Monitoring**
   - Live dashboard with WebSocket updates
   - Instant anomaly alerts
   - Recent logs viewer with auto-refresh

---

## 🏗️ Architecture & Technology Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Groq (llama-3.3-70b-versatile) | Log analysis, anomaly reasoning |
| **Orchestration** | LangGraph | Workflow management (8 nodes) |
| **Backend** | FastAPI | Async REST API + WebSocket |
| **Database** | MongoDB (Motor) | Logs, KPIs, anomalies storage |
| **Vector DB** | Pinecone | Embedding storage, semantic search |
| **Embeddings** | sentence-transformers | Text → 384-dim vectors |
| **Frontend** | HTML + Tailwind CSS | Real-time dashboard |
| **Validation** | Pydantic | Type-safe data models |

### LangGraph Workflow (8 Nodes)

```
┌─────────────────────────────────────────────────────────────┐
│                    Log Ingestion (POST /logs)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 1: Input Validation                                    │
│  • Validates log structure with Pydantic                     │
│  • Ensures required fields present                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 2: KPI Extraction                                      │
│  • Extracts: endpoint, method, status, latency              │
│  • Adds timestamp and metadata                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 3: LLM Analysis                                        │
│  • Calls Groq LLM for intelligent analysis                   │
│  • Tracks token usage and cost                              │
│  • Generates natural language summary                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 4: Anomaly Detection                                   │
│  • Statistical analysis (z-score, IQR)                       │
│  • LLM-based pattern recognition                             │
│  • Assigns severity level                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 5: MongoDB Persistence                                 │
│  • Stores in api_logs collection                             │
│  • Stores anomalies separately                               │
│  • Creates indexes for fast queries                          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 6: Embedding Generation                                │
│  • Converts log to text representation                       │
│  • Generates 384-dim vector (sentence-transformers)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 7: Pinecone Storage                                    │
│  • Upserts embedding to vector database                      │
│  • Stores metadata for filtering                             │
│  • Enables semantic search                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Node 8: Response Formatting                                 │
│  • Prepares final API response                               │
│  • Includes analysis, anomaly flags, processing time         │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    Return Response to Client
```

---

## 📦 Prerequisites

### Required Software

1. **Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **MongoDB**
   - Local installation OR
   - MongoDB Atlas (cloud) OR
   - Docker container

3. **API Keys**
   - **Groq API Key**: Get from [console.groq.com](https://console.groq.com)
   - **Pinecone API Key**: Get from [pinecone.io](https://www.pinecone.io)

### Optional but Recommended

- **Docker** (for easy MongoDB setup)
- **Git** (for version control)
- **Virtual Environment** (venv or conda)

---

## 🚀 Installation Guide

### Step 1: Clone/Navigate to Project

```bash
cd "c:\Users\lenovo\OneDrive\Desktop\AI Agents\llm-kpi-montoring"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI, Uvicorn (web framework)
- Motor, PyMongo (MongoDB drivers)
- Pinecone (vector database)
- Groq (LLM client)
- LangGraph, LangChain (orchestration)
- sentence-transformers (embeddings)
- Pydantic (validation)

**Note**: First run may take 5-10 minutes as sentence-transformers downloads the embedding model (~400MB).

### Step 4: Set Up MongoDB

**Option A: Docker (Easiest)**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Option B: Local Installation**
- Download from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
- Install and start service

**Option C: MongoDB Atlas (Cloud)**
- Create free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
- Get connection string

### Step 5: Configure Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit .env with your actual values
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

---

## ⚙️ Configuration

### Environment Variables Explained

Open `.env` and configure:

```bash
# ============================================
# GROQ LLM CONFIGURATION
# ============================================
# Get your API key from: https://console.groq.com
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# ============================================
# MONGODB CONFIGURATION
# ============================================
# Local MongoDB:
MONGO_CONNECTION_STRING=mongodb://localhost:27017

# MongoDB Atlas (cloud):
# MONGO_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/

# Database name (will be created automatically)
DB_NAME=llm_kpi_monitoring

# ============================================
# PINECONE CONFIGURATION
# ============================================
# Get your API key from: https://www.pinecone.io
PINECONE_API_KEY=your_pinecone_api_key_here

# Region (e.g., us-east1-gcp, us-west1-gcp)
PINECONE_ENVIRONMENT=us-east1-gcp

# Index name (will be created automatically)
PINECONE_INDEX_NAME=api-logs-embeddings

# ============================================
# EMBEDDING MODEL
# ============================================
# sentence-transformers model name
LOCAL_EMBED_MODEL=sentence-transformers/all-mpnet-base-v2

# ============================================
# APPLICATION SETTINGS
# ============================================
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# ============================================
# COST TRACKING (USD per 1M tokens)
# ============================================
# Groq pricing for llama-3.3-70b-versatile
GROQ_COST_PER_1M_INPUT_TOKENS=0.59
GROQ_COST_PER_1M_OUTPUT_TOKENS=0.79
```

### Important Notes

- **GROQ_API_KEY**: Required for LLM analysis
- **PINECONE_API_KEY**: Required for semantic search
- **MONGO_CONNECTION_STRING**: Must be accessible from your machine
- **PINECONE_ENVIRONMENT**: Must match your Pinecone region

---

## 📁 Project Structure Explained

```
llm-kpi-montoring/
│
├── config/                          # Existing configuration modules
│   ├── logger.py                    # Centralized logging setup
│   ├── database.py                  # MongoDB connection management
│   └── pinecone.py                  # Pinecone connection management
│
├── database/                        # Database client implementations
│   ├── __init__.py
│   ├── mongodb.py                   # Async MongoDB operations
│   │   ├── MongoDBClient class
│   │   ├── insert_log(), get_logs_in_timerange()
│   │   ├── insert_anomaly(), get_anomalies()
│   │   └── Connection pooling & indexing
│   │
│   └── pinecone_client.py           # Vector database operations
│       ├── PineconeClient class
│       ├── upsert_embedding(), search_similar_logs()
│       └── Metadata filtering
│
├── models/                          # Pydantic data models (type-safe)
│   ├── __init__.py
│   ├── log_models.py                # API log schemas
│   │   ├── APILogRequest (incoming logs)
│   │   ├── APILogDocument (MongoDB schema)
│   │   └── LogMetadata
│   │
│   ├── kpi_models.py                # KPI metric schemas
│   │   ├── KPIMetrics (latency, rates, counts)
│   │   ├── LLMMetrics (tokens, costs)
│   │   └── AnomalyScore
│   │
│   └── response_models.py           # API response schemas
│       ├── LogIngestionResponse
│       ├── KPIResponse
│       └── AnomalyListResponse
│
├── services/                        # Business logic layer
│   ├── __init__.py
│   ├── llm_service.py               # Groq LLM integration
│   │   ├── analyze_log() - AI analysis
│   │   ├── detect_anomaly_with_llm() - LLM-based detection
│   │   └── Token tracking & cost estimation
│   │
│   ├── embedding_service.py         # Text → Vector conversion
│   │   ├── generate_embedding() - Creates 384-dim vectors
│   │   ├── embed_query() - Helper function
│   │   └── Uses sentence-transformers
│   │
│   ├── kpi_service.py               # Metrics calculation
│   │   ├── get_aggregated_kpis() - Calculate metrics
│   │   ├── get_llm_metrics() - LLM usage stats
│   │   └── Statistical aggregations
│   │
│   └── anomaly_service.py           # Anomaly detection
│       ├── detect_anomaly() - Main detection logic
│       ├── Statistical methods (z-score, IQR)
│       └── LLM enhancement
│
├── workflows/                       # LangGraph orchestration
│   ├── __init__.py
│   └── monitoring_graph.py          # 8-node workflow
│       ├── MonitoringState (TypedDict)
│       ├── 8 async node functions
│       ├── create_monitoring_graph()
│       └── process_log() - Main entry point
│
├── routes/                          # FastAPI endpoints (no business logic)
│   ├── __init__.py
│   ├── logs.py                      # POST /logs, GET /logs/recent
│   ├── kpis.py                      # GET /kpis, /kpis/llm-metrics
│   ├── anomalies.py                 # GET /anomalies, /anomalies/count
│   └── websocket.py                 # WS /live-kpis (real-time)
│
├── utils/                           # Helper functions & constants
│   ├── __init__.py
│   ├── config.py                    # Pydantic Settings (env vars)
│   ├── prompts.py                   # LLM prompt templates
│   │   ├── SYSTEM_PROMPT
│   │   ├── LOG_ANALYSIS_PROMPT
│   │   └── ANOMALY_DETECTION_PROMPT
│   │
│   └── metrics.py                   # Statistical functions
│       ├── calculate_percentile(), calculate_mean()
│       ├── detect_anomaly_zscore(), detect_anomaly_iqr()
│       └── estimate_llm_cost()
│
├── static/                          # Frontend assets
│   └── dashboard.html               # Real-time monitoring dashboard
│       ├── Tailwind CSS styling
│       ├── WebSocket client
│       └── Live KPI updates
│
├── logs/                            # Application logs (auto-created)
│   └── neuroqueue.log               # Centralized log file
│
├── main.py                          # FastAPI application bootstrap
│   ├── Lifespan management (startup/shutdown)
│   ├── Database connections
│   ├── Router registration
│   ├── CORS middleware
│   └── Health check endpoints
│
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (YOU CREATE)
├── .env.example                     # Environment template
├── README.md                        # Original project specification
└── SETUP.md                         # This file!
```

### Key Design Principles

1. **Separation of Concerns**
   - Routes: Handle HTTP requests/responses only
   - Services: Contain all business logic
   - Models: Define data structures
   - Workflows: Orchestrate complex operations

2. **Type Safety**
   - Pydantic models everywhere
   - TypedDict for workflow state
   - Full type hints in function signatures

3. **Async First**
   - All I/O operations are async
   - Non-blocking database calls
   - Concurrent LLM requests possible

4. **Centralized Configuration**
   - All settings in `config/` and `utils/config.py`
   - Environment-based configuration
   - No hardcoded values

---

## 🔧 How It Works

### End-to-End Flow Example

**Scenario**: Your application sends an API log to the monitoring system.

#### 1. **Log Submission**

Your application makes a POST request:

```python
import requests

log_data = {
    "endpoint": "/api/checkout",
    "method": "POST",
    "status_code": 500,
    "latency": 3500.0,
    "error": "Database connection timeout",
    "user_id": "user_12345",
    "trace_id": "abc-def-123"
}

response = requests.post(
    "http://localhost:8000/logs",
    json=log_data
)

print(response.json())
```

#### 2. **LangGraph Workflow Execution**

The system processes the log through 8 nodes:

**Node 1 - Validation**: ✅ Log structure valid
**Node 2 - KPI Extraction**: Extracted endpoint, status=500, latency=3500ms
**Node 3 - LLM Analysis**: 
```
"CRITICAL: Server error with extremely high latency (3500ms). 
Database timeout indicates potential connection pool exhaustion 
or database overload. Immediate investigation required."
```
**Node 4 - Anomaly Detection**: 
- Statistical: Latency 7x above P95 → Anomaly
- LLM: Confirms critical severity
- **Result**: `is_anomaly=True, severity=CRITICAL`

**Node 5 - MongoDB**: Stored in collections:
- `api_logs` (all logs)
- `anomalies` (flagged issues)

**Node 6 - Embedding**: Generated 384-dim vector from log text

**Node 7 - Pinecone**: Stored vector with metadata for future similarity search

**Node 8 - Response**: Formatted final response

#### 3. **Response Returned**

```json
{
  "success": true,
  "log_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "analysis_summary": "CRITICAL: Server error with extremely high latency...",
  "is_anomaly": true,
  "anomaly_severity": "CRITICAL",
  "processing_time_ms": 487.3
}
```

#### 4. **Real-Time Dashboard Update**

- WebSocket broadcasts anomaly alert to all connected dashboards
- Alert appears with red CRITICAL badge
- KPI metrics update to reflect new data
- Recent logs table shows the new entry

#### 5. **Future Semantic Search**

Later, you can find similar incidents:

```python
# Find logs similar to this critical error
similar_logs = pinecone_client.search_similar_logs(
    query_vector=embedding_vector,
    top_k=5,
    filter_metadata={"anomaly_severity": "CRITICAL"}
)
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### 1. Health Check

```http
GET /
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T06:30:00Z",
  "services": {
    "mongodb": "connected",
    "pinecone": "connected",
    "llm": "groq-llama-3.3-70b"
  }
}
```

#### 2. Ingest Log

```http
POST /logs
Content-Type: application/json
```

**Request Body:**
```json
{
  "endpoint": "/api/users",           // Required
  "method": "GET",                    // Required
  "status_code": 200,                 // Required (100-599)
  "latency": 145.5,                   // Required (milliseconds)
  "error": null,                      // Optional
  "user_id": "user123",               // Optional
  "trace_id": "abc-def-123",          // Optional
  "headers": {},                      // Optional
  "metadata": {}                      // Optional
}
```

**Response:**
```json
{
  "success": true,
  "log_id": "65a1b2c3d4e5f6g7h8i9j0k1",
  "analysis_summary": "Normal request. Latency within expected range.",
  "is_anomaly": false,
  "anomaly_severity": null,
  "processing_time_ms": 234.5
}
```

#### 3. Get Recent Logs

```http
GET /logs/recent?limit=100&endpoint=/api/users
```

**Query Parameters:**
- `limit` (optional): Number of logs (default: 100, max: 500)
- `endpoint` (optional): Filter by specific endpoint

**Response:**
```json
{
  "success": true,
  "count": 50,
  "logs": [
    {
      "_id": "65a1b2c3d4e5f6g7h8i9j0k1",
      "endpoint": "/api/users",
      "method": "GET",
      "status_code": 200,
      "latency": 145.5,
      "timestamp": "2026-01-18T06:30:00Z",
      "is_anomaly": false,
      "llm_analysis": "Normal request..."
    }
  ]
}
```

#### 4. Get KPI Metrics

```http
GET /kpis?time_range=1h&endpoint=/api/users
```

**Query Parameters:**
- `time_range` (optional): `1h`, `24h`, `7d`, `30d` (default: `1h`)
- `endpoint` (optional): Filter by specific endpoint

**Response:**
```json
{
  "success": true,
  "kpi_metrics": {
    "total_requests": 1500,
    "success_count": 1450,
    "error_count": 50,
    "success_rate": 96.67,
    "error_rate": 3.33,
    "avg_latency": 125.5,
    "p50_latency": 110.0,
    "p95_latency": 250.0,
    "p99_latency": 450.0,
    "max_latency": 3500.0,
    "time_range": "1h",
    "start_time": "2026-01-18T05:30:00Z",
    "end_time": "2026-01-18T06:30:00Z",
    "endpoint": null
  }
}
```

#### 5. Get LLM Metrics

```http
GET /kpis/llm-metrics?time_range=24h
```

**Response:**
```json
{
  "success": true,
  "llm_metrics": {
    "total_llm_calls": 1500,
    "total_input_tokens": 450000,
    "total_output_tokens": 75000,
    "total_cost": 0.32,
    "avg_llm_latency": 234.5,
    "time_range": "24h"
  }
}
```

#### 6. Get Endpoint Breakdown

```http
GET /kpis/breakdown?time_range=1h
```

**Response:**
```json
{
  "success": true,
  "breakdown": {
    "/api/users": { /* KPI metrics */ },
    "/api/checkout": { /* KPI metrics */ },
    "/api/products": { /* KPI metrics */ }
  }
}
```

#### 7. Get Anomalies

```http
GET /anomalies?severity=HIGH&time_range=24h&limit=50
```

**Query Parameters:**
- `severity` (optional): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `time_range` (optional): `1h`, `24h`, `7d`, `30d`
- `limit` (optional): Max results (default: 50, max: 500)

**Response:**
```json
{
  "success": true,
  "total_count": 12,
  "anomalies": [
    {
      "log_id": "65a1b2c3...",
      "endpoint": "/api/checkout",
      "method": "POST",
      "status_code": 500,
      "latency": 3500.0,
      "timestamp": "2026-01-18T06:15:00Z",
      "anomaly_score": {
        "is_anomaly": true,
        "severity": "CRITICAL",
        "confidence": 0.95,
        "reason": "Latency 10x above P95, server error",
        "z_score": 7.2
      },
      "llm_analysis": "CRITICAL: Server error with extremely high latency..."
    }
  ],
  "time_range": "24h"
}
```

#### 8. Get Anomaly Count

```http
GET /anomalies/count?time_range=1h
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "time_range": "1h"
}
```

#### 9. WebSocket - Live KPIs

```javascript
const ws = new WebSocket('ws://localhost:8000/live-kpis');

ws.onopen = () => {
  console.log('Connected');
  
  // Request data
  ws.send('get_kpis');
  ws.send('get_recent_logs');
  
  // Heartbeat
  setInterval(() => ws.send('ping'), 15000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'initial_kpis':
      // First KPI data on connection
      console.log('Initial KPIs:', data.data);
      break;
      
    case 'kpi_update':
      // Periodic KPI updates
      console.log('Updated KPIs:', data.data);
      break;
      
    case 'recent_logs':
      // Recent logs response
      console.log('Recent logs:', data.data);
      break;
      
    case 'new_log':
      // Real-time new log notification
      console.log('New log:', data.data);
      break;
      
    case 'anomaly_alert':
      // Real-time anomaly alert
      console.log('ANOMALY:', data.data);
      break;
  }
};
```

---

## 🖥️ Dashboard Usage

### Accessing the Dashboard

1. Start the application:
   ```bash
   python main.py
   ```

2. Open browser:
   ```
   http://localhost:8000/static/dashboard.html
   ```

### Dashboard Features

#### 1. **Connection Status**
- **Green pulsing dot**: Connected to WebSocket
- **Red dot**: Disconnected (auto-reconnects)

#### 2. **KPI Cards** (Top Row)

**Total Requests**
- Shows total API requests in last hour
- Updates every 10 seconds

**Success Rate**
- Percentage of 2xx responses
- Green color indicates healthy

**Average Latency**
- Mean response time
- Shows P95 latency below

**Anomalies**
- Count of detected issues
- Red color for visibility

#### 3. **Anomaly Alerts** (Middle Section)

- Appears when anomalies detected
- Color-coded by severity:
  - 🔴 **CRITICAL**: Red border
  - 🟠 **HIGH**: Orange border
  - 🟡 **MEDIUM**: Yellow border
  - 🔵 **LOW**: Blue border
- Shows LLM analysis
- Auto-dismisses after 30 seconds

#### 4. **Recent Logs Table** (Bottom)

Columns:
- **Timestamp**: When log was received
- **Endpoint**: API path
- **Method**: HTTP method
- **Status**: Color-coded (green=2xx, yellow=4xx, red=5xx)
- **Latency**: Response time in ms
- **Anomaly**: Badge if flagged

Features:
- Auto-updates with new logs
- Click "Refresh" for manual update
- Shows last 50 logs

### Dashboard Controls

**Manual Refresh**
```javascript
// Click "Refresh" button or send WebSocket message
ws.send('get_recent_logs');
```

**Request KPI Update**
```javascript
ws.send('get_kpis');
```

---

## 🧪 Testing & Verification

### Quick Test Script

Create `test_system.py`:

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Test 1: Health Check
print("1. Testing health check...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: Normal Log
print("2. Sending normal log...")
normal_log = {
    "endpoint": "/api/users",
    "method": "GET",
    "status_code": 200,
    "latency": 150.0
}
response = requests.post(f"{BASE_URL}/logs", json=normal_log)
print(f"   Response: {response.json()}\n")

# Test 3: Anomalous Log (High Latency)
print("3. Sending anomalous log (high latency)...")
anomaly_log = {
    "endpoint": "/api/checkout",
    "method": "POST",
    "status_code": 200,
    "latency": 5000.0  # Very high latency
}
response = requests.post(f"{BASE_URL}/logs", json=anomaly_log)
print(f"   Response: {response.json()}\n")

# Test 4: Error Log
print("4. Sending error log...")
error_log = {
    "endpoint": "/api/payment",
    "method": "POST",
    "status_code": 500,
    "latency": 3500.0,
    "error": "Database connection timeout"
}
response = requests.post(f"{BASE_URL}/logs", json=error_log)
print(f"   Response: {response.json()}\n")

# Wait for processing
time.sleep(2)

# Test 5: Get KPIs
print("5. Fetching KPIs...")
response = requests.get(f"{BASE_URL}/kpis?time_range=1h")
print(f"   KPIs: {response.json()}\n")

# Test 6: Get Anomalies
print("6. Fetching anomalies...")
response = requests.get(f"{BASE_URL}/anomalies?time_range=1h")
print(f"   Anomalies: {response.json()}\n")

print("✅ All tests completed!")
```

Run it:
```bash
python test_system.py
```

### Expected Results

1. ✅ Health check returns 200
2. ✅ Normal log: `is_anomaly=False`
3. ✅ High latency log: `is_anomaly=True, severity=HIGH/CRITICAL`
4. ✅ Error log: `is_anomaly=True, severity=CRITICAL`
5. ✅ KPIs show aggregated metrics
6. ✅ Anomalies list shows flagged logs

### Verification Checklist

- [ ] Application starts without errors
- [ ] MongoDB connection successful
- [ ] Pinecone connection successful
- [ ] Dashboard loads and shows "Connected"
- [ ] Can submit logs via API
- [ ] LLM analysis appears in responses
- [ ] Anomalies detected correctly
- [ ] Dashboard updates in real-time
- [ ] WebSocket reconnects after disconnect

---

## 🔍 Troubleshooting

### Common Issues

#### 1. **Import Error: No module named 'sentence_transformers'**

**Solution:**
```bash
pip install sentence-transformers
```

First run downloads ~400MB model, be patient.

#### 2. **MongoDB Connection Failed**

**Error:**
```
Failed to connect to MongoDB: ...
```

**Solutions:**
- Check MongoDB is running: `docker ps` or `mongod --version`
- Verify `MONGO_CONNECTION_STRING` in `.env`
- Test connection: `mongosh "mongodb://localhost:27017"`

#### 3. **Pinecone API Error**

**Error:**
```
Failed to connect to Pinecone: Unauthorized
```

**Solutions:**
- Verify `PINECONE_API_KEY` is correct
- Check `PINECONE_ENVIRONMENT` matches your Pinecone region
- Ensure Pinecone account is active

#### 4. **Groq API Error**

**Error:**
```
LLM analysis failed: 401 Unauthorized
```

**Solutions:**
- Verify `GROQ_API_KEY` in `.env`
- Check API key at [console.groq.com](https://console.groq.com)
- Ensure you have API credits

#### 5. **Dashboard Not Loading**

**Error:**
```
404 Not Found
```

**Solutions:**
- Ensure `static/dashboard.html` exists
- Check URL: `http://localhost:8000/static/dashboard.html`
- Verify FastAPI mounted static files correctly

#### 6. **WebSocket Disconnects Immediately**

**Solutions:**
- Check browser console for errors
- Verify WebSocket URL: `ws://localhost:8000/live-kpis`
- Ensure no firewall blocking WebSocket connections

#### 7. **Slow First Request**

**Cause:** sentence-transformers loading model into memory

**Solution:** This is normal. Subsequent requests will be fast.

### Debug Mode

Enable detailed logging:

```bash
# In .env
LOG_LEVEL=DEBUG
```

Check logs:
```bash
cat logs/neuroqueue.log
```

---

## 🚀 Advanced Usage

### Custom Embedding Model

Change embedding model in `.env`:

```bash
# Options:
# - sentence-transformers/all-mpnet-base-v2 (384 dim) - Default
# - sentence-transformers/all-MiniLM-L6-v2 (384 dim) - Faster
# - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384 dim) - Multilingual

LOCAL_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Important:** If changing dimension, update Pinecone index dimension in `database/pinecone_client.py`.

### Batch Log Ingestion

For high-volume scenarios:

```python
import asyncio
import httpx

async def batch_ingest_logs(logs):
    async with httpx.AsyncClient() as client:
        tasks = [
            client.post("http://localhost:8000/logs", json=log)
            for log in logs
        ]
        responses = await asyncio.gather(*tasks)
    return responses

# Usage
logs = [
    {"endpoint": "/api/users", "method": "GET", "status_code": 200, "latency": 100},
    {"endpoint": "/api/products", "method": "GET", "status_code": 200, "latency": 150},
    # ... more logs
]

asyncio.run(batch_ingest_logs(logs))
```

### Custom Anomaly Thresholds

Edit `services/anomaly_service.py`:

```python
# Line ~50
is_latency_anomaly, z_score = detect_anomaly_zscore(
    value=latency,
    mean=kpi_metrics.avg_latency,
    std=max(kpi_metrics.p95_latency - kpi_metrics.avg_latency, 1.0),
    threshold=2.5  # Change this (default: 2.5)
)
```

Lower threshold = more sensitive (more anomalies)
Higher threshold = less sensitive (fewer anomalies)

### Semantic Search Example

```python
from services.embedding_service import embed_query
from database.pinecone_client import pinecone_client

# Find logs similar to a query
query = "database timeout error high latency"
query_vector = embed_query(query)

similar_logs = await pinecone_client.search_similar_logs(
    query_vector=query_vector,
    top_k=5,
    filter_metadata={"anomaly_severity": "CRITICAL"}
)

for log in similar_logs:
    print(f"Score: {log['score']}, Endpoint: {log['metadata']['endpoint']}")
```

### Production Deployment

**Recommendations:**

1. **Use Production ASGI Server**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **Enable HTTPS**
   - Use reverse proxy (Nginx, Caddy)
   - Configure SSL certificates

3. **Database Scaling**
   - MongoDB: Use replica sets
   - Pinecone: Use production tier

4. **Monitoring**
   - Add Prometheus metrics
   - Set up alerts for anomalies

5. **Rate Limiting**
   - Add FastAPI rate limiting middleware
   - Protect against abuse

---

## 📊 Performance Metrics

### Expected Performance

| Operation | Latency | Notes |
|-----------|---------|-------|
| Log Ingestion | 200-500ms | Includes LLM call |
| KPI Calculation | 50-100ms | Depends on data volume |
| Anomaly Detection | 100-300ms | With LLM enhancement |
| Semantic Search | 50-150ms | Pinecone query |
| Dashboard Update | <50ms | WebSocket broadcast |

### Optimization Tips

1. **Disable LLM for High Volume**
   - Set `use_llm=False` in anomaly detection
   - Reduces latency by ~200ms

2. **Batch Embeddings**
   - Use `batch_generate_embeddings()` for multiple logs
   - More efficient than individual calls

3. **Cache KPIs**
   - Implement Redis caching for frequently accessed KPIs
   - Reduce MongoDB queries

---

## 🎓 Learning Resources

### Understanding the Code

1. **Start Here:**
   - `main.py` - Application entry point
   - `workflows/monitoring_graph.py` - Core workflow
   - `routes/logs.py` - Simple API endpoint

2. **Key Concepts:**
   - **LangGraph**: [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
   - **FastAPI**: [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
   - **Pydantic**: [Pydantic Docs](https://docs.pydantic.dev/)

3. **Modify & Extend:**
   - Add new KPI metrics in `utils/metrics.py`
   - Create custom prompts in `utils/prompts.py`
   - Add new endpoints in `routes/`

---

## 📞 Support & Contact

### Getting Help

1. **Check Logs:**
   ```bash
   tail -f logs/neuroqueue.log
   ```

2. **Review Documentation:**
   - This SETUP.md
   - `walkthrough.md` in artifacts
   - `implementation_plan.md` in artifacts

3. **Common Commands:**
   ```bash
   # Restart application
   python main.py
   
   # Check MongoDB
   mongosh "mongodb://localhost:27017"
   
   # Test API
   curl http://localhost:8000/health
   ```

---

## ✅ Quick Start Checklist

- [ ] Python 3.9+ installed
- [ ] MongoDB running
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with API keys
- [ ] Application starts without errors
- [ ] Dashboard accessible at `http://localhost:8000/static/dashboard.html`
- [ ] Test log submitted successfully
- [ ] KPIs visible on dashboard
- [ ] WebSocket connected (green dot)

---

## 🎉 Congratulations!

You now have a fully functional, production-ready LLM KPI Monitoring System!

**Next Steps:**
1. Integrate with your applications to send logs
2. Customize anomaly detection thresholds
3. Set up alerts for critical anomalies
4. Monitor LLM costs and optimize prompts
5. Scale to production workloads

**Happy Monitoring! 🚀**
