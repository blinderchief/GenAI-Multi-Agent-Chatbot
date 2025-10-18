# Aria Chatbot - API Documentation

## Base URL
```
http://localhost:8000
```

---

## Endpoints

### 1. Health Check

#### `GET /`
Root endpoint - basic health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-18T10:30:00.000000"
}
```

---

#### `GET /health`
Detailed health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-10-18T10:30:00.000000"
}
```

---

### 2. Chat

#### `POST /chat`
Send a message to Aria and get a response

**Request Body:**
```json
{
  "message": "What is LangChain?",
  "session_id": "optional-session-id"
}
```

**Parameters:**
- `message` (string, required): The user's message
- `session_id` (string, optional): Session identifier. If not provided, a new session will be created

**Response:**
```json
{
  "response": "LangChain is a framework for developing applications powered by language models...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "confidence": 0.92,
  "sources": [
    {
      "title": "What is LangChain?",
      "url": "https://python.langchain.com/",
      "type": "curated",
      "relevance": 0.95
    }
  ],
  "metadata": {
    "type": "standard",
    "retrieval_sources": 3,
    "web_sources": 1,
    "evaluation": {
      "hallucination_score": 0.05,
      "relevance_score": 0.95
    }
  },
  "timestamp": "2025-10-18T10:30:00.000000"
}
```

**Response Fields:**
- `response` (string): Aria's response to the user
- `session_id` (string): Session identifier for conversation continuity
- `confidence` (float): Confidence score (0.0 - 1.0)
- `sources` (array): List of sources used to generate the response
- `metadata` (object): Additional information about the response
- `timestamp` (string): ISO format timestamp

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Processing error

**Example cURL:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is RAG?",
    "session_id": "my-session-123"
  }'
```

**Special Response Types:**

1. **Introduction** (first message in session):
```json
{
  "response": "Hi! I'm Aria Voss, a GenAI enthusiast...",
  "metadata": {
    "type": "introduction"
  }
}
```

2. **Clarifying Questions**:
```json
{
  "response": "Before I answer, let me clarify a few things:\n1. ...\n2. ...\n3. ...",
  "metadata": {
    "type": "clarifying_questions"
  }
}
```

3. **Redirect** (non-GenAI topic):
```json
{
  "response": "That's an interesting question, but I specialize in Generative AI...",
  "metadata": {
    "type": "redirect",
    "reason": "non_genai_topic"
  }
}
```

---

### 3. Conversation History

#### `GET /conversation/{session_id}`
Retrieve conversation history for a session

**Parameters:**
- `session_id` (string, required): Session identifier (path parameter)

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "role": "assistant",
      "content": "Hi! I'm Aria...",
      "timestamp": "2025-10-18T10:30:00.000000"
    },
    {
      "role": "user",
      "content": "What is LangChain?",
      "timestamp": "2025-10-18T10:30:15.000000"
    },
    {
      "role": "assistant",
      "content": "LangChain is a framework...",
      "timestamp": "2025-10-18T10:30:18.000000"
    }
  ],
  "message_count": 3
}
```

**Status Codes:**
- `200 OK`: Success
- `500 Internal Server Error`: Retrieval error

**Example cURL:**
```bash
curl http://localhost:8000/conversation/my-session-123
```

---

### 4. Clear Conversation

#### `DELETE /conversation/{session_id}`
Clear conversation history for a session

**Parameters:**
- `session_id` (string, required): Session identifier (path parameter)

**Response:**
```json
{
  "message": "Conversation my-session-123 cleared successfully"
}
```

**Status Codes:**
- `200 OK`: Success
- `404 Not Found`: Session not found
- `500 Internal Server Error`: Deletion error

**Example cURL:**
```bash
curl -X DELETE http://localhost:8000/conversation/my-session-123
```

---

### 5. Persona

#### `GET /persona`
Get Aria's persona information

**Response:**
```json
{
  "name": "Aria Voss",
  "role": "Research Analyst specializing in Generative AI",
  "background": "28-year-old with a master's in CS from MIT, focusing on ML and NLP",
  "interests": [
    "AI libraries",
    "emerging GenAI models",
    "research papers",
    "industry trends"
  ],
  "style": "Friendly, curious, and thoughtful"
}
```

**Status Codes:**
- `200 OK`: Success

**Example cURL:**
```bash
curl http://localhost:8000/persona
```

---

## Interactive API Documentation

FastAPI provides interactive documentation:

### Swagger UI
Visit: http://localhost:8000/docs

Features:
- Try out all endpoints directly in browser
- See request/response schemas
- View example values
- Test authentication (if enabled)

### ReDoc
Visit: http://localhost:8000/redoc

Features:
- Clean, readable documentation
- Download as OpenAPI spec
- Better for sharing with team

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error description here"
}
```

**Common Errors:**

1. **500 Internal Server Error**
```json
{
  "detail": "Failed to process message: Connection timeout"
}
```

2. **422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production:

Recommended limits:
- 100 requests per minute per IP
- 1000 requests per hour per session

---

## Authentication

Currently no authentication is required. For production, consider:

- API key authentication
- JWT tokens
- OAuth2

Example with API key:
```bash
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?"}'
```

---

## CORS

CORS is configured to allow all origins in development:
```python
allow_origins=["*"]
```

For production, specify exact origins:
```python
allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
]
```

---

## Webhooks

Not currently implemented. Future enhancement for:
- Real-time notifications
- Conversation events
- Evaluation results

---

## SDKs & Client Libraries

### Python Client Example:

Install dependencies with uv:
```bash
uv pip install requests
```

```python
import requests

class AriaClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, message):
        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "message": message,
                "session_id": self.session_id
            }
        )
        data = response.json()
        self.session_id = data["session_id"]
        return data
    
    def get_history(self):
        if not self.session_id:
            return None
        response = requests.get(
            f"{self.base_url}/conversation/{self.session_id}"
        )
        return response.json()
    
    def clear(self):
        if not self.session_id:
            return
        requests.delete(
            f"{self.base_url}/conversation/{self.session_id}"
        )
        self.session_id = None

# Usage
client = AriaClient()
response = client.chat("What is LangChain?")
print(response["response"])
```

### JavaScript Client Example:

```javascript
class AriaClient {
    constructor(baseUrl = "http://localhost:8000") {
        this.baseUrl = baseUrl;
        this.sessionId = null;
    }
    
    async chat(message) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        const data = await response.json();
        this.sessionId = data.session_id;
        return data;
    }
    
    async getHistory() {
        if (!this.sessionId) return null;
        const response = await fetch(
            `${this.baseUrl}/conversation/${this.sessionId}`
        );
        return await response.json();
    }
    
    async clear() {
        if (!this.sessionId) return;
        await fetch(
            `${this.baseUrl}/conversation/${this.sessionId}`,
            { method: "DELETE" }
        );
        this.sessionId = null;
    }
}

// Usage
const client = new AriaClient();
const response = await client.chat("What is LangChain?");
console.log(response.response);
```

---

## Performance

**Typical Response Times:**
- Health check: < 10ms
- Chat (with retrieval): 1-3 seconds
- Chat (with web scraping): 3-5 seconds
- Conversation history: < 50ms

**Optimization Tips:**
1. Use session IDs to maintain context
2. Disable web scraping for faster responses
3. Reduce `RETRIEVAL_TOP_K` for faster retrieval
4. Use local LLMs (Ollama) to avoid API latency
5. Enable caching for frequent queries

---

## Monitoring

Recommended monitoring:
- Response times per endpoint
- Error rates
- LLM API usage
- Qdrant query performance
- Session count and duration

Logs location: `logs/aria.log`

---

## Version History

**v1.0.0** (Current)
- Initial release
- All 5 agents functional
- FastAPI + Streamlit
- Qdrant integration
- Multi-LLM support

---

## Support

For API issues:
1. Check `/health` endpoint
2. Review `logs/aria.log`
3. Verify environment variables
4. Check Qdrant connection
5. Validate LLM API keys

---

**API Documentation Last Updated:** October 18, 2025
