# Cost Breakdown & Optimization Strategies for Suyash GenAI Chatbot

## Technical Architecture

### System Overview
Suyash is a multi-agent AI chatbot built with a microservices architecture:

**Frontend Layer**
- **Streamlit** web application (Python-based UI)
- Handles user interactions and displays chat interface
- Communicates with backend via REST API

**Backend Layer**
- **FastAPI** REST API server
- Orchestrates multiple AI agents using **LangChain** and **LangGraph**
- Agents: Retrieval, Web Scraper, Reasoning, Memory, Evaluation

**Data Layer**
- **Qdrant Cloud** vector database for knowledge storage and semantic search
- **SerpAPI** for real-time web search capabilities

**AI/ML Layer**
- **Google Gemini** (gemini-2.0-flash) for text generation
- **Sentence Transformers** (all-MiniLM-L6-v2) for embeddings
- **PyTorch** runtime for model inference

---

## Technologies Used

### Core Stack
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI 0.104+ | High-performance async API |
| Frontend Framework | Streamlit | Rapid UI development |
| AI Orchestration | LangChain 0.1+ | LLM workflow management |
| AI Framework | LangGraph 0.0.20+ | Multi-agent coordination |
| Vector Database | Qdrant Cloud | Semantic search & memory |
| LLM Provider | Google Gemini API | Text generation |
| Embeddings | Sentence Transformers | Vector representations |
| Web Scraping | Playwright, BeautifulSoup4, SerpAPI | Real-time data retrieval |
| Validation | Pydantic v2 | Data validation & settings |

### Supporting Libraries
- **httpx**: Async HTTP client
- **python-multipart**: File upload handling
- **transformers**: HuggingFace model integration
- **torch**: Deep learning runtime
- **ragas**: Response quality evaluation
- **langsmith**: Observability & debugging

---

## Current Hosting Approach (Local Development)

### Deployment Model
- **Backend**: Runs on `localhost:8000` (uvicorn server)
- **Frontend**: Runs on `localhost:8501` (Streamlit server)
- **Database**: Qdrant Cloud (managed SaaS)
- **Compute**: Local machine (CPU-based inference)

### Resource Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum (8GB recommended for smooth operation)
- **Storage**: ~2GB for models and dependencies
- **Network**: Stable internet for API calls (Gemini, Qdrant Cloud, SerpAPI)

---

## Cost Breakdown (Current Setup)

### Monthly Operating Costs

| Service | Tier | Cost | Usage Cap |
|---------|------|------|-----------|
| **Google Gemini API** | Pay-as-you-go | ~$0.00025/1K chars (input)<br>~$0.001/1K chars (output) | Varies by usage |
| **Qdrant Cloud** | Free Tier | $0 | 1GB storage, unlimited queries |
| **SerpAPI** | Free Trial | $0 (then $50/mo) | 100 searches/mo free, then paid |
| **Hosting** | Local | $0 | N/A |
| **Compute** | Local | $0 (electricity cost only) | N/A |

**Estimated Monthly Cost**: **$0-10** (depending on API usage)

### Cost Drivers
1. **LLM API Calls** (Gemini): ~70% of variable costs
2. **Web Search** (SerpAPI): ~20% after free tier
3. **Vector Database** (Qdrant): $0 on free tier
4. **Hosting**: $0 (local deployment)

---

## Production Hosting Options & Costs

### Option 1: Cloud VMs (Recommended for MVP)
**Provider**: AWS EC2, Azure VM, Google Compute Engine

**Architecture**:
- Backend: `t3.medium` (2 vCPU, 4GB RAM) - $30/mo
- Frontend: Same instance or separate `t3.small` - $15/mo
- Load Balancer: AWS ALB - $20/mo
- Total: **~$65/mo** + API costs

**Pros**: Full control, easy scaling
**Cons**: Manual DevOps, security management

---

### Option 2: Serverless (Cost-Optimized)
**Provider**: AWS Lambda + API Gateway, Azure Functions

**Architecture**:
- Backend API: AWS Lambda (Python) - Pay per request
- Frontend: AWS Amplify or Vercel - $0-20/mo
- Database: Keep Qdrant Cloud free tier
- Cold start mitigation: Provisioned concurrency - $15/mo

**Cost Estimate**:
- 10K requests/mo: **~$15/mo**
- 100K requests/mo: **~$50/mo**

**Pros**: Auto-scaling, pay-per-use
**Cons**: Cold starts, 15min timeout limits

---

### Option 3: Container Platform (Scalable)
**Provider**: AWS ECS Fargate, Azure Container Instances, Google Cloud Run

**Architecture**:
- Backend: Cloud Run (0.5 vCPU, 1GB RAM) - $12/mo base
- Frontend: Cloud Run (0.25 vCPU, 512MB) - $8/mo
- Total: **~$20-40/mo** + API costs

**Pros**: Auto-scaling, no server management
**Cons**: Container image management

---

### Option 4: Kubernetes (Enterprise)
**Provider**: AWS EKS, Azure AKS, Google GKE

**Architecture**:
- Cluster: 2 nodes (t3.medium) - $60/mo
- Load Balancer: $20/mo
- Monitoring: Prometheus/Grafana - $0-30/mo
- Total: **~$80-150/mo**

**Pros**: Production-grade, multi-tenant
**Cons**: High complexity, DevOps overhead

---

## Optimization Strategies

### 1. API Cost Reduction (60-80% savings potential)

#### A. LLM Optimization
```python
# Current: Full conversation context sent every time
# Optimized: Summarize old messages, send only recent + summary

def optimize_context(messages, max_tokens=2000):
    if token_count(messages) > max_tokens:
        # Keep last 5 messages, summarize older ones
        recent = messages[-5:]
        old_summary = summarize(messages[:-5])
        return [old_summary] + recent
    return messages
```

**Savings**: ~50% reduction in input tokens

#### B. Caching Strategy
```python
# Cache embeddings for frequently asked questions
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str):
    return embedding_model.encode(text)
```

**Savings**: ~30% reduction in embedding API calls

#### C. Model Tiering
```python
# Use cheaper models for simple queries
def select_model(query_complexity):
    if complexity == "simple":
        return "gemini-1.5-flash"  # 50% cheaper
    else:
        return "gemini-2.0-flash"
```

**Savings**: ~25% on LLM costs

---

### 2. Qdrant Optimization (Stay in free tier)

#### A. Vector Compression
```python
# Reduce embedding dimensions 384 → 256
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
# Apply PCA or quantization to reduce storage
```

**Savings**: ~33% storage reduction

#### B. Smart Indexing
```python
# Only index recent conversations, archive old ones
def archive_old_sessions(days=30):
    cutoff = datetime.now() - timedelta(days=days)
    # Move to cheaper cold storage or delete
```

**Savings**: Keep within 1GB free tier limit

#### C. Query Optimization
```python
# Reduce top_k to minimum needed
RETRIEVAL_TOP_K = 3  # Instead of 5
# Use scroll API for bulk operations
```

**Savings**: ~20% faster queries, lower compute

---

### 3. Infrastructure Cost Optimization

#### A. Auto-Scaling Rules
```yaml
# Example for Cloud Run
scaling:
  minInstances: 0  # Scale to zero when idle
  maxInstances: 10
  targetConcurrency: 80
```

**Savings**: ~70% on idle time costs

#### B. Spot Instances (VMs)
```bash
# Use AWS Spot for 70% discount on non-critical workloads
aws ec2 run-instances --instance-type t3.medium --spot-price 0.01
```

**Savings**: Up to 70% on compute

#### C. Regional Optimization
- Host backend in same region as Qdrant Cloud (eu-central-1)
- Use CDN for static frontend assets
- **Savings**: ~20% latency reduction, lower data transfer costs

---

### 4. Development & Monitoring Optimization

#### A. Local Caching for Development
```python
# .env configuration
ENABLE_CACHING=true
CACHE_TTL_SECONDS=3600  # Already configured
```

#### B. Request Batching
```python
# Process multiple embeddings in one call
def batch_embed(texts: List[str], batch_size=32):
    for i in range(0, len(texts), batch_size):
        yield embedding_model.encode(texts[i:i+batch_size])
```

**Savings**: ~15% faster, lower overhead

#### C. Monitoring & Alerts
```python
# Track costs in real-time
import logging

def log_api_cost(provider, tokens, cost):
    logger.info(f"{provider}: {tokens} tokens = ${cost:.4f}")
    # Alert if daily budget exceeded
```

---

## Recommended Production Architecture (Cost-Optimized)

### Target: $30-50/month for 10K-50K requests

```
┌─────────────────────────────────────────────────┐
│          Users (Web Browser)                     │
└─────────────────┬───────────────────────────────┘
                  │
         ┌────────▼────────┐
         │   Cloudflare    │  Free tier (CDN + DDoS)
         │   or Vercel     │
         └────────┬────────┘
                  │
    ┌─────────────▼─────────────┐
    │  Frontend (Streamlit)      │  Cloud Run: $8/mo
    │  - Static assets cached    │
    │  - Auto-scales to 0        │
    └─────────────┬──────────────┘
                  │ REST API
    ┌─────────────▼──────────────┐
    │  Backend (FastAPI)         │  Cloud Run: $20/mo
    │  - Containerized           │  - 0.5 vCPU, 1GB RAM
    │  - Auto-scales 0-10        │  - Min instances: 0
    │  - Request caching         │
    └──┬──────────┬──────────┬───┘
       │          │          │
   ┌───▼───┐  ┌──▼───┐  ┌──▼────┐
   │Gemini │  │Qdrant│  │SerpAPI│
   │ API   │  │Cloud │  │       │
   │$5/mo  │  │ Free │  │$0-50  │
   └───────┘  └──────┘  └───────┘
```

**Total Cost**: **$33-83/month** (scales with usage)

---

## Implementation Roadmap

### Phase 1: Immediate Optimizations (Week 1)
- [ ] Enable request caching (`ENABLE_CACHING=true`)
- [ ] Reduce `RETRIEVAL_TOP_K` to 3
- [ ] Implement embedding caching
- [ ] Add cost logging for API calls

**Expected Savings**: 20-30% on API costs

### Phase 2: Code Optimizations (Week 2-3)
- [ ] Implement context summarization
- [ ] Add model tiering based on query complexity
- [ ] Batch embedding requests
- [ ] Compress vector dimensions

**Expected Savings**: 40-50% on API costs

### Phase 3: Production Deployment (Week 4-6)
- [ ] Containerize backend and frontend
- [ ] Deploy to Google Cloud Run
- [ ] Set up auto-scaling rules
- [ ] Configure monitoring and alerts
- [ ] Migrate to production Qdrant tier if needed

**Expected Cost**: $30-50/month

### Phase 4: Advanced Optimizations (Month 2+)
- [ ] Implement hybrid search (vector + keyword)
- [ ] Add response caching for common queries
- [ ] Use cheaper models for classification tasks
- [ ] Implement request rate limiting
- [ ] Set up A/B testing for model selection

**Expected Savings**: 60-70% total cost reduction

---

## Cost Monitoring Dashboard (Recommended Tools)

1. **LangSmith** (LangChain official)
   - Track LLM token usage
   - Monitor latency and errors
   - Free tier: 5K traces/month

2. **Prometheus + Grafana** (Open source)
   - Custom metrics for API costs
   - Real-time alerting
   - Free (self-hosted)

3. **Cloud Provider Tools**
   - Google Cloud Billing (built-in)
   - AWS Cost Explorer
   - Azure Cost Management

---

## Final Recommendations

### For Current Local Setup:
1. Keep using Qdrant Cloud free tier
2. Monitor Gemini API usage closely
3. Implement caching (already configured in code)
4. Use SerpAPI sparingly (only when needed)

**Estimated Monthly Cost**: **$5-15**

### For Production Deployment:
1. **Best ROI**: Google Cloud Run + Qdrant Cloud
2. **Implement**: Auto-scaling, caching, model tiering
3. **Monitor**: Set up alerts for daily budget ($2-3/day max)
4. **Scale**: Add paid Qdrant tier only if hitting free limits

**Estimated Monthly Cost**: **$30-80** (depending on traffic)

### Break-Even Analysis:
- **100 users/day × 5 messages = 500 requests/day**
- Cloud Run: $25/mo (fully utilized)
- APIs: $15/mo (with optimizations)
- **Total: $40/mo** ≈ **$0.08 per user** or **$0.0016 per message**

---

## Next Steps

Would you like me to:
1. Create a detailed deployment guide for any specific platform?
2. Generate Infrastructure-as-Code (Terraform/Pulumi) for the recommended architecture?
3. Build a cost monitoring script to track daily API spending?
4. Implement any of the optimization strategies in your current codebase?
