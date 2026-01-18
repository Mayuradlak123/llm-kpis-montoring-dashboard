# LLM KPI Monitoring System

A production-ready API monitoring system powered by Large Language Models (Groq/Llama 3), LangGraph, and Vector Databases (Pinecone).

## 🚀 Features

*   **Real-time Dashboard**: Live "Matrix-style" monitoring of API health.
*   **AI Analysis**: Every log analyzed by Llama 3 for sentiment, errors, and insights.
*   **Anomaly Detection**: Statistical (z-score) and semantic anomaly detection.
*   **Vector Search**: Semantic storage of logs in Pinecone.
*   **Cost Tracking**: Token usage and cost estimation.

## 🛠️ Tech Stack

*   **Backend**: FastAPI, Python 3.9+
*   **AI Orchestraion**: LangGraph, LangChain
*   **LLM**: Groq (Llama 3.3-70b)
*   **Database**: MongoDB (Logs/KPIs), Pinecone (Vectors)
*   **Frontend**: HTML5, Tailwind CSS, WebSockets

## 🔌 Integration Guide: How to Connect Your App

You can connect **any** software application (Python, Node.js, Java, Go, etc.) to this monitoring system. 
Simply send a `POST` request to the `/logs` endpoint whenever your app handles a request.

### 1. Python Integration (e.g., FastAPI/Flask/Django)

```python
import requests
import time

def log_to_monitor(endpoint, method, status_code, start_time):
    latency = (time.time() - start_time) * 1000  # ms
    
    payload = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "latency": latency,
        "response_size": 1024,  # Optional
        "error": None           # Optional error message
    }
    
    try:
        # Send to the monitoring system (assuming running locally)
        requests.post("http://localhost:8000/logs", json=payload)
    except Exception as e:
        print(f"Failed to log: {e}")

# Usage Example
start = time.time()
# ... process your API request ...
log_to_monitor("/api/generate-email", "POST", 200, start)
```

### 2. Node.js Integration (e.g., Express/NestJS)

```javascript
const axios = require('axios');

async function logToMonitor(endpoint, method, statusCode, startTime) {
    const latency = Date.now() - startTime;
    
    const payload = {
        endpoint: endpoint,
        method: method,
        status_code: statusCode,
        latency: latency,
        response_size: 512,
        error: null
    };

    try {
        await axios.post('http://localhost:8000/logs', payload);
    } catch (error) {
        console.error('Monitoring failed:', error.message);
    }
}

// Usage Example
const start = Date.now();
// ... handle request ...
logToMonitor('/api/chat', 'POST', 200, start);
```

## 📦 Setup & Installation

1.  **Clone the repository**
2.  **Install dependencies**: `pip install -r requirements.txt`
3.  **Configure Environment**:
    *   Rename `.env.example` to `.env`
    *   Add your Groq API Key
    *   Add MongoDB URI
    *   Add Pinecone API Key
4.  **Run the System**:
    *   Linux/Mac: `./run.sh`
    *   Windows: `python main.py`

## 📊 Dashboard

Access the live dashboard at: `http://localhost:8000/`

## 🧪 Testing

Run the test data generator to see it in action:
```bash
python test_data_generator.py continuous 1
```
