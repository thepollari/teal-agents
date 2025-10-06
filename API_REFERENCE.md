# Teal Agents Framework - API Reference

## Overview

The Teal Agents Framework exposes RESTful APIs and WebSocket endpoints for agent interaction, orchestration, and management. This reference documents all available endpoints, request/response formats, authentication methods, and integration patterns.

## Base URLs and Versioning

### Service Endpoints

| Service | Default Port | Base URL | Purpose |
|---------|--------------|----------|---------|
| Core Framework | 8000 | `http://localhost:8000` | Agent execution |
| Assistant Orchestrator | 8001 | `http://localhost:8001` | Chat orchestration |
| AO Services | 8002 | `http://localhost:8002` | Agent catalog |
| Collaboration Orchestrator | 8003 | `http://localhost:8003` | Multi-agent workflows |

### API Versioning

The framework uses configuration-based API versioning:

- **`skagents/v1`** → AppV1 endpoints
- **`skagents/v2alpha1`** → AppV2 endpoints  
- **`tealagents/v1alpha1`** → AppV3 endpoints

## Core Framework API (sk-agents)

### Agent Execution Endpoints

#### POST /{AgentName}/{AgentVersion}/

Execute an agent with the specified configuration.

**URL Pattern**: `/{AgentName}/{AgentVersion}/`

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <token> (optional)
```

**Request Body**:
```json
{
  "chat_history": [
    {
      "role": "user",
      "content": "Hello, how can you help me?"
    }
  ],
  "additional_context": "Optional context information",
  "user_id": "user123" // For stateful agents
}
```

**Response**:
```json
{
  "response": "I'm here to help! What would you like to know?",
  "metadata": {
    "agent_name": "SimpleAgent",
    "agent_version": "1.0",
    "execution_time": 1.23,
    "model_used": "gpt-4o",
    "tokens_used": {
      "prompt": 45,
      "completion": 23,
      "total": 68
    }
  },
  "session_id": "session_abc123" // For stateful agents
}
```

**Status Codes**:
- `200 OK` - Successful execution
- `400 Bad Request` - Invalid input format
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Agent not found
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Execution error

#### POST /{AgentName}/{AgentVersion}/sse

Server-Sent Events streaming endpoint for real-time responses.

**URL Pattern**: `/{AgentName}/{AgentVersion}/sse`

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
Accept: text/event-stream
```

**Request Body**: Same as regular execution endpoint

**Response Stream**:
```
event: start
data: {"session_id": "session_abc123", "agent_name": "SimpleAgent"}

event: token
data: {"token": "I'm", "position": 0}

event: token
data: {"token": " here", "position": 1}

event: complete
data: {"response": "I'm here to help!", "metadata": {...}}

event: error
data: {"error": "Error message", "code": "ERROR_CODE"}
```

**Event Types**:
- `start` - Execution started
- `token` - Streaming token (for compatible models)
- `complete` - Execution completed
- `error` - Error occurred

#### WebSocket /ws/{AgentName}/{AgentVersion}/

**Note**: WebSocket endpoints are deprecated. Use SSE for streaming.

### Multi-Modal Endpoints (AppV2)

#### POST /{AgentName}/{AgentVersion}/multimodal

Handle multi-modal inputs including images and text.

**Request Body**:
```json
{
  "inputs": [
    {
      "type": "text",
      "content": "What do you see in this image?"
    },
    {
      "type": "image",
      "content": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
      "format": "base64"
    }
  ],
  "chat_history": [...],
  "user_id": "user123"
}
```

**Response**:
```json
{
  "response": "I can see a beautiful landscape with mountains and a lake.",
  "metadata": {
    "processed_inputs": ["text", "image"],
    "image_analysis": {
      "detected_objects": ["mountain", "lake", "sky"],
      "confidence_scores": [0.95, 0.89, 0.92]
    }
  }
}
```

### Agent-to-Agent Communication (A2A)

#### POST /{AgentName}/{AgentVersion}/a2a

Enable agent-to-agent communication for collaborative workflows.

**Request Body**:
```json
{
  "source_agent": "AgentA",
  "target_agent": "AgentB",
  "message": "Please analyze this data",
  "context": {
    "task_id": "task_123",
    "workflow_step": 2
  },
  "data": {
    "analysis_results": [...]
  }
}
```

**Response**:
```json
{
  "response": "Analysis completed",
  "forwarded_to": "AgentB",
  "correlation_id": "corr_456",
  "metadata": {
    "processing_time": 2.34,
    "next_agent": "AgentC"
  }
}
```

## Health and Status Endpoints

### GET /health

Basic health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.2.3",
  "uptime": 3600
}
```

### GET /ready

Readiness probe for container orchestration.

**Response**:
```json
{
  "ready": true,
  "dependencies": {
    "redis": "connected",
    "database": "connected",
    "llm_provider": "available"
  }
}
```

### GET /metrics

Prometheus-compatible metrics endpoint.

**Response**:
```
# HELP teal_agents_requests_total Total number of requests
# TYPE teal_agents_requests_total counter
teal_agents_requests_total{agent="SimpleAgent",status="success"} 1234

# HELP teal_agents_request_duration_seconds Request duration
# TYPE teal_agents_request_duration_seconds histogram
teal_agents_request_duration_seconds_bucket{le="0.1"} 100
teal_agents_request_duration_seconds_bucket{le="0.5"} 450
teal_agents_request_duration_seconds_bucket{le="1.0"} 800
```

## Assistant Orchestrator API

### Chat Orchestration

#### POST /chat

Initiate a chat session with agent selection.

**Request Body**:
```json
{
  "message": "I need help with Python programming",
  "user_id": "user123",
  "session_id": "session_abc123", // Optional, for continuing sessions
  "preferences": {
    "preferred_agents": ["PythonExpert", "CodeReviewer"],
    "response_style": "detailed"
  }
}
```

**Response**:
```json
{
  "response": "I can help you with Python! What specific topic would you like to explore?",
  "selected_agent": {
    "name": "PythonExpert",
    "version": "2.1",
    "confidence": 0.95,
    "reasoning": "Best match for Python programming queries"
  },
  "session_id": "session_abc123",
  "alternatives": [
    {
      "name": "CodeReviewer",
      "confidence": 0.78,
      "reasoning": "Good for code analysis"
    }
  ]
}
```

#### POST /chat/stream

Streaming chat with real-time agent selection.

**Headers**:
```
Accept: text/event-stream
```

**Response Stream**:
```
event: agent_selection
data: {"selected_agent": "PythonExpert", "confidence": 0.95}

event: response_start
data: {"session_id": "session_abc123"}

event: token
data: {"token": "I", "position": 0}

event: response_complete
data: {"full_response": "I can help you with Python!", "metadata": {...}}
```

### Agent Management

#### GET /agents

List available agents in the catalog.

**Query Parameters**:
- `category` - Filter by agent category
- `tags` - Filter by tags (comma-separated)
- `search` - Search in agent names and descriptions

**Response**:
```json
{
  "agents": [
    {
      "name": "PythonExpert",
      "version": "2.1",
      "description": "Expert in Python programming and best practices",
      "category": "programming",
      "tags": ["python", "coding", "debugging"],
      "capabilities": ["code_generation", "code_review", "debugging"],
      "status": "active",
      "last_updated": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 10
}
```

#### GET /agents/{agent_name}

Get detailed information about a specific agent.

**Response**:
```json
{
  "name": "PythonExpert",
  "version": "2.1",
  "description": "Expert in Python programming and best practices",
  "category": "programming",
  "tags": ["python", "coding", "debugging"],
  "capabilities": ["code_generation", "code_review", "debugging"],
  "configuration": {
    "model": "gpt-4o",
    "max_tokens": 2000,
    "temperature": 0.7
  },
  "plugins": ["PythonPlugin", "CodeAnalysisPlugin"],
  "status": "active",
  "metrics": {
    "total_requests": 1234,
    "success_rate": 0.98,
    "avg_response_time": 1.45
  }
}
```

#### POST /agents/{agent_name}/test

Test an agent with sample input.

**Request Body**:
```json
{
  "test_input": "Write a Python function to calculate fibonacci numbers",
  "expected_output": "Should return a function implementation",
  "test_type": "functionality"
}
```

**Response**:
```json
{
  "test_result": "passed",
  "actual_output": "def fibonacci(n): ...",
  "execution_time": 1.23,
  "score": 0.95,
  "feedback": "Function correctly implements fibonacci calculation"
}
```

## Collaboration Orchestrator API

### Workflow Management

#### POST /workflows

Create a new multi-agent workflow.

**Request Body**:
```json
{
  "name": "Document Analysis Workflow",
  "description": "Analyze documents using multiple specialized agents",
  "steps": [
    {
      "id": "extract",
      "agent": "DocumentExtractor",
      "input_mapping": {
        "document": "workflow.input.document"
      }
    },
    {
      "id": "analyze",
      "agent": "ContentAnalyzer",
      "input_mapping": {
        "text": "steps.extract.output.text"
      },
      "depends_on": ["extract"]
    }
  ],
  "output_mapping": {
    "analysis": "steps.analyze.output.analysis",
    "summary": "steps.analyze.output.summary"
  }
}
```

**Response**:
```json
{
  "workflow_id": "workflow_123",
  "status": "created",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_duration": 30
}
```

#### POST /workflows/{workflow_id}/execute

Execute a workflow with input data.

**Request Body**:
```json
{
  "input": {
    "document": "base64-encoded-document-content"
  },
  "options": {
    "timeout": 300,
    "retry_failed_steps": true,
    "parallel_execution": true
  }
}
```

**Response**:
```json
{
  "execution_id": "exec_456",
  "status": "running",
  "started_at": "2024-01-15T10:35:00Z",
  "progress": {
    "completed_steps": 0,
    "total_steps": 2,
    "current_step": "extract"
  }
}
```

#### GET /workflows/{workflow_id}/executions/{execution_id}

Get workflow execution status and results.

**Response**:
```json
{
  "execution_id": "exec_456",
  "workflow_id": "workflow_123",
  "status": "completed",
  "started_at": "2024-01-15T10:35:00Z",
  "completed_at": "2024-01-15T10:36:30Z",
  "duration": 90,
  "steps": [
    {
      "id": "extract",
      "status": "completed",
      "agent": "DocumentExtractor",
      "duration": 45,
      "output": {
        "text": "Extracted document content...",
        "metadata": {...}
      }
    },
    {
      "id": "analyze",
      "status": "completed",
      "agent": "ContentAnalyzer",
      "duration": 45,
      "output": {
        "analysis": "Document analysis results...",
        "summary": "Brief summary..."
      }
    }
  ],
  "output": {
    "analysis": "Document analysis results...",
    "summary": "Brief summary..."
  }
}
```

### Team Orchestration

#### POST /teams

Create a team of agents for collaborative tasks.

**Request Body**:
```json
{
  "name": "Research Team",
  "description": "Team for conducting research tasks",
  "members": [
    {
      "agent": "ResearchAgent",
      "role": "researcher",
      "capabilities": ["web_search", "data_analysis"]
    },
    {
      "agent": "WriterAgent", 
      "role": "writer",
      "capabilities": ["content_creation", "summarization"]
    }
  ],
  "manager": "ManagerAgent",
  "communication_pattern": "hub_and_spoke"
}
```

**Response**:
```json
{
  "team_id": "team_789",
  "status": "created",
  "members": 2,
  "manager": "ManagerAgent"
}
```

#### POST /teams/{team_id}/tasks

Assign a task to a team.

**Request Body**:
```json
{
  "task": "Research the latest developments in AI and write a summary",
  "requirements": {
    "max_length": 1000,
    "sources_required": 5,
    "deadline": "2024-01-16T10:00:00Z"
  },
  "priority": "high"
}
```

**Response**:
```json
{
  "task_id": "task_101",
  "status": "assigned",
  "assigned_to": "team_789",
  "estimated_completion": "2024-01-15T12:00:00Z"
}
```

## Authentication and Authorization

### API Key Authentication

Include API key in request headers:

```
Authorization: Bearer your-api-key-here
```

Or as query parameter:
```
GET /agents?api_key=your-api-key-here
```

### JWT Authentication

For stateful agents and user sessions:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**JWT Payload**:
```json
{
  "user_id": "user123",
  "session_id": "session_abc123",
  "permissions": ["agent_execute", "workflow_create"],
  "exp": 1642248000,
  "iat": 1642244400
}
```

### OAuth 2.0 Integration

For enterprise deployments:

```
Authorization: Bearer oauth-access-token
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input format",
    "details": {
      "field": "chat_history",
      "reason": "Required field missing"
    },
    "request_id": "req_123456",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request format |
| `AUTHENTICATION_ERROR` | 401 | Invalid or missing credentials |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions |
| `AGENT_NOT_FOUND` | 404 | Specified agent doesn't exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `EXECUTION_ERROR` | 500 | Agent execution failed |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

### Default Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Agent Execution | 100 requests | 1 minute |
| Chat API | 50 requests | 1 minute |
| Workflow Creation | 10 requests | 1 minute |
| Agent Catalog | 200 requests | 1 minute |

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642244460
X-RateLimit-Window: 60
```

## WebHooks

### Workflow Completion Webhook

Configure webhook URL to receive notifications:

**POST to your webhook URL**:
```json
{
  "event": "workflow.completed",
  "workflow_id": "workflow_123",
  "execution_id": "exec_456",
  "status": "completed",
  "timestamp": "2024-01-15T10:36:30Z",
  "data": {
    "duration": 90,
    "output": {...}
  }
}
```

### Agent Status Webhook

**POST to your webhook URL**:
```json
{
  "event": "agent.status_changed",
  "agent_name": "PythonExpert",
  "old_status": "active",
  "new_status": "maintenance",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDK and Client Libraries

### Python SDK

```python
from teal_agents import TealAgentsClient

client = TealAgentsClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Execute agent
response = client.execute_agent(
    agent_name="SimpleAgent",
    agent_version="1.0",
    input_data={
        "chat_history": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)

# Stream response
for token in client.stream_agent(
    agent_name="SimpleAgent",
    agent_version="1.0",
    input_data={"chat_history": [...]}
):
    print(token)
```

### JavaScript SDK

```javascript
import { TealAgentsClient } from '@teal-agents/client';

const client = new TealAgentsClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Execute agent
const response = await client.executeAgent({
  agentName: 'SimpleAgent',
  agentVersion: '1.0',
  inputData: {
    chat_history: [
      { role: 'user', content: 'Hello!' }
    ]
  }
});

// Stream response
const stream = client.streamAgent({
  agentName: 'SimpleAgent',
  agentVersion: '1.0',
  inputData: { chat_history: [...] }
});

for await (const token of stream) {
  console.log(token);
}
```

### cURL Examples

#### Execute Agent

```bash
curl -X POST http://localhost:8000/SimpleAgent/1.0/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "chat_history": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

#### Stream Response

```bash
curl -X POST http://localhost:8000/SimpleAgent/1.0/sse \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "chat_history": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

#### List Agents

```bash
curl -X GET http://localhost:8001/agents \
  -H "Authorization: Bearer your-api-key" \
  -G -d "category=programming" -d "tags=python"
```

This comprehensive API reference provides all the information needed to integrate with and extend the Teal Agents Framework programmatically.
