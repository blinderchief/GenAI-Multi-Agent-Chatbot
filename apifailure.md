# API Failure Mitigation Plan: 6 Hours Before Submission

## Scenario
The API you're using suddenly goes down 6 hours before submission. You've built half your product around it.

---

## Step-by-Step Action Plan

### **Hour 0-1: Immediate Assessment & Triage (First 60 minutes)**

#### Step 1: Identify Critical vs. Non-Critical Dependencies (15 min)
**Technical Actions:**
```bash
# Quick audit of which APIs are down and impact
- Google Gemini API (LLM) → CRITICAL - core reasoning
- SerpAPI (web search) → MEDIUM - can fallback to knowledge base only
- Qdrant Cloud → CRITICAL - but has 99.9% SLA, unlikely to fail
```

**Team Communication:**
- **Slack/Discord message to all team members:** 
  > "🚨 CRITICAL: [API_NAME] is down. Emergency meeting in 5 min. Stop current work. Join [meeting link]."
- Assign roles immediately:
  - **You (lead):** Technical decision-making
  - **Backend dev:** Implement fallback
  - **Frontend dev:** Update UI to handle degraded mode
  - **Tester:** Validate fallback functionality

#### Step 2: Determine Root Cause & ETA (15 min)
**Technical Actions:**
- Check API status page (e.g., status.openai.com, status.google.com)
- Check Twitter/Reddit for outage reports
- Test with different API keys to rule out account issues
- Check our rate limits/quotas

**Decision Tree:**
```
Is there an official ETA?
├─ Yes, <2 hours → WAIT mode (continue other work)
├─ Yes, 2-4 hours → HYBRID mode (prepare fallback + hope for recovery)
└─ No ETA or >4 hours → FALLBACK mode (switch immediately)
```

#### Step 3: Activate Fallback Strategy (30 min)
**For Gemini API Failure (Most Likely Scenario):**

**Option A: Switch to OpenAI GPT-4o-mini (fastest, 20 min)**
```python
# backend/app/services/llm_service.py
# Already have OpenAI in requirements.txt

from openai import OpenAI

class LLMService:
    def __init__(self):
        # Add emergency fallback
        self.primary_provider = os.getenv("LLM_PROVIDER", "gemini")
        self.fallback_provider = "openai"
        
        try:
            if self.primary_provider == "gemini":
                self.client = ChatGoogleGenerativeAI(...)
        except Exception as e:
            logger.error(f"Primary LLM failed: {e}, switching to {self.fallback_provider}")
            self.client = ChatOpenAI(
                model="gpt-4o-mini",  # Cheap fallback
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.7
            )
```

**Quick .env update:**
```bash
# Add to .env (use free trial key or team member's personal key)
OPENAI_API_KEY=sk-proj-...
LLM_FALLBACK_PROVIDER=openai
```

**Option B: Use Local Model (slower, 40 min setup but zero API dependency)**
```python
# If OpenAI also fails, use Ollama locally
from langchain_community.llms import Ollama

self.client = Ollama(
    model="llama3.1:8b",  # Fast, good quality
    temperature=0.7
)
```

```bash
# One team member installs Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1:8b  # 5GB download, ~10 min
```

---

### **Hour 1-3: Implementation & Testing (Next 2 hours)**

#### Step 4: Implement Fallback with Graceful Degradation (60 min)

**Code Changes:**

**1. Update LLM Service with Auto-Retry Logic:**
```python
# backend/app/services/llm_service.py

class LLMService:
    def generate(self, prompt: str, max_retries=3):
        providers = [self.primary_provider, self.fallback_provider, "local"]
        
        for attempt, provider in enumerate(providers):
            try:
                if provider == "gemini":
                    response = self.gemini_client.invoke(prompt)
                elif provider == "openai":
                    response = self.openai_client.invoke(prompt)
                else:  # local fallback
                    response = self.ollama_client.invoke(prompt)
                
                logger.info(f"✓ Response generated using {provider}")
                return response
                
            except Exception as e:
                logger.warning(f"✗ {provider} failed (attempt {attempt+1}): {e}")
                if attempt == len(providers) - 1:
                    # All providers failed - return graceful error
                    return "I'm experiencing technical difficulties. Please try again in a moment."
        
        return response
```

**2. Add Status Banner in Frontend:**
```python
# frontend/app.py

def check_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.json().get("llm_provider") != "gemini":
            return "degraded"
    except:
        return "down"
    return "healthy"

status = check_api_health()

if status == "degraded":
    st.warning("⚠️ We're experiencing issues with our primary AI service. Responses may be slower but functionality is maintained.")
elif status == "down":
    st.error("🔴 Service temporarily unavailable. Our team is working on a fix.")
```

**3. Add Health Endpoint to Report Fallback Status:**
```python
# backend/main.py

@app.get("/health")
async def health_check():
    llm_status = "healthy"
    current_provider = llm_service.get_active_provider()
    
    if current_provider != settings.model_provider:
        llm_status = "degraded"
    
    return {
        "status": "healthy" if llm_status == "healthy" else "degraded",
        "llm_provider": current_provider,
        "fallback_active": current_provider != settings.model_provider,
        "timestamp": datetime.now(timezone.utc)
    }
```

#### Step 5: Rapid Testing Protocol (30 min)

**Test Matrix:**
```bash
# Create test script: scripts/emergency_test.py

test_cases = [
    "What is RAG?",  # Simple query
    "Compare LangChain vs LangGraph",  # Complex reasoning
    "Latest news on GPT-5",  # Web search trigger
]

for query in test_cases:
    response = send_chat_request(query)
    assert response.status_code == 200
    assert len(response.json()["response"]) > 50
    print(f"✓ {query[:30]}... passed")
```

**Testing Checklist:**
- [ ] Basic Q&A works
- [ ] Sources still shown
- [ ] Conversation memory preserved
- [ ] Response quality acceptable (not perfect, but good enough)
- [ ] No crashes or 500 errors
- [ ] Frontend shows degraded status banner

#### Step 6: Team Communication & Documentation (30 min)

**Internal Update:**
```
📢 Team Update (Hour 2):

STATUS: Fallback implemented and tested ✅

CHANGES:
- Switched from Gemini → OpenAI GPT-4o-mini
- Response time: ~3s (vs 2s normally)
- Quality: 85-90% of original (acceptable for demo)
- Cost: +$0.20/100 requests (we can afford it for demo)

KNOWN ISSUES:
- Slight response quality drop (less creative)
- Web search still works fine
- All core features functional

DEMO TALKING POINTS:
- Highlight resilient architecture
- Show fallback mechanism as a FEATURE
- Emphasize: "Production-ready with high availability"

NEXT ACTIONS:
- Backend: Monitor logs for errors
- Frontend: Final UI polish
- Everyone: Run through demo script 2x
```

---

### **Hour 3-5: Polish & Demo Prep (Next 2 hours)**

#### Step 7: Turn Crisis into Feature (45 min)

**Reframe the Narrative:**
Instead of hiding the outage, showcase resilience as a competitive advantage.

**Add to Demo Script:**
> "One thing that makes Suyash production-ready is its fault-tolerant architecture. 
> Notice in the health endpoint, we're currently running on our fallback LLM provider. 
> If our primary API goes down, the system automatically switches to a backup with zero downtime. 
> This is critical for enterprise deployments where 99.9% uptime is required."

**Add Visual Indicator (Optional):**
```python
# frontend/app.py - sidebar

with st.sidebar:
    health = check_api_health()
    if health == "degraded":
        st.info("💡 **Resilient Mode Active**\nAutomatic fallback to backup AI service")
```

#### Step 8: Prepare Backup Demo Environment (45 min)

**Contingency Plan:**
```bash
# If even fallback fails, prepare offline demo

1. Record 3-5 key demo interactions NOW while system works
2. Save as JSON responses
3. Create "demo mode" that plays back recorded interactions

# backend/main.py
DEMO_MODE = os.getenv("DEMO_MODE", "false") == "true"
DEMO_RESPONSES = {
    "what is rag": {...saved response...},
    "compare langchain langraph": {...saved response...},
}

if DEMO_MODE and query.lower() in DEMO_RESPONSES:
    return DEMO_RESPONSES[query.lower()]
```

**Why:** If everything fails during live demo, you can still showcase functionality

#### Step 9: Create Emergency Communication Templates (30 min)

**For Judges/Audience (if asked about the issue):**
> "Great question! We actually encountered a production outage with our primary LLM provider 
> during development, which gave us an opportunity to implement a real-world failover system. 
> As you can see, the chatbot is still fully functional using our backup provider. 
> This kind of resilience is exactly what production systems need, and it's baked into our architecture."

**For README/Submission Form:**
```markdown
## High Availability Architecture

Suyash implements automatic failover across multiple LLM providers:
- Primary: Google Gemini (cost-optimized)
- Fallback: OpenAI GPT-4o-mini (reliability)
- Emergency: Local Ollama (zero API dependency)

Health monitoring and automatic provider switching ensure 99.9% uptime.
```

---

### **Hour 5-6: Final Checks & Submission (Last hour)**

#### Step 10: Pre-Submission Checklist (30 min)

**Technical:**
- [ ] All critical features work (tested 3x)
- [ ] Demo environment stable
- [ ] Backup demo mode ready (if needed)
- [ ] Logs show no critical errors
- [ ] Health endpoint returns 200

**Submission Materials:**
- [ ] README updated with resilience features
- [ ] Architecture diagram shows fallback paths
- [ ] Video demo recorded (in case live demo fails)
- [ ] Screenshots of working system
- [ ] Cost breakdown updated for new API

**Team:**
- [ ] Everyone knows their role in demo
- [ ] Practiced demo script 2x
- [ ] Backup person ready to present if needed

#### Step 11: Submit Early (20 min)

**DO NOT wait until last minute:**
- Submit at Hour 5:40, not 5:59
- Allows time for upload issues, form bugs, etc.
- Better to submit "good enough" on time than "perfect" late

#### Step 12: Post-Submission Debrief (10 min)

**Team huddle:**
```
✅ What worked:
- Fast decision-making
- Clear role assignments
- Fallback strategy worked

⚠️ What to improve:
- Should have tested failover BEFORE crisis
- Need better monitoring/alerts

🎓 Lessons learned:
- Always have Plan B (and C)
- Communicate early and often
- Turn problems into features
```

---

## Key Principles for Crisis Management

### 1. **Speed over Perfection**
- 80% solution in 2 hours > 100% solution in 6 hours
- Ship working code, not perfect code

### 2. **Communication is Critical**
- Update team every 30-60 minutes
- Be transparent about trade-offs
- Assign clear ownership

### 3. **Leverage What You Have**
- Use team members' personal API keys
- Borrow credits from friends if needed
- Use free trials aggressively

### 4. **Turn Lemons into Lemonade**
- Frame outage as "resilience testing"
- Showcase your problem-solving skills
- Demonstrate production-ready thinking

### 5. **Always Have a Backup**
- Record demo videos early
- Prepare offline demo mode
- Have screenshots of working features

---

## Specific to Suyash Project

### Most Likely Failure: Google Gemini API Down

**30-Minute Mitigation:**
```bash
# 1. Add OpenAI key to .env (5 min)
echo "OPENAI_API_KEY=sk-proj-xxx" >> .env

# 2. Update llm_service.py with fallback logic (10 min)
# 3. Test with 3 queries (5 min)
# 4. Update frontend health check (5 min)
# 5. Quick team sync (5 min)
```

**Result:** Fully functional system with 10-15% quality drop (acceptable)

### Least Likely Failure: Qdrant Cloud Down

**60-Minute Mitigation:**
```bash
# 1. Export all vectors from Qdrant (15 min)
python scripts/backup_qdrant.py

# 2. Spin up local Qdrant in Docker (10 min)
docker run -p 6333:6333 qdrant/qdrant

# 3. Import vectors to local instance (15 min)
python scripts/restore_qdrant.py

# 4. Update QDRANT_URL in .env (5 min)
# 5. Test retrieval agent (10 min)
# 6. Deploy local Qdrant to cloud VM if needed (5 min - optional)
```

---

## Success Metrics

**Technical:**
- System functional with degraded mode: ✅
- No critical errors in logs: ✅
- Response time <5 seconds: ✅

**Team:**
- Everyone knows their role: ✅
- Confidence in demo: ✅
- Submission on time: ✅

**Perception:**
- Turned crisis into strength: ✅
- Demonstrated resilience: ✅
- Impressed judges: ✅

---

## The Bottom Line

**6 hours is enough time to pivot IF:**
1. You have modular, well-architected code
2. You communicate clearly and quickly
3. You focus on "good enough" not "perfect"
4. You leverage your team effectively
5. You reframe the problem as an opportunity

**The goal isn't to hide the failure—it's to showcase how you handle it. That's what separates good engineers from great ones.**