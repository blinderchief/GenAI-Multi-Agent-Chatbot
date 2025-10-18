# Quick Start Guide - Aria Chatbot

## 🚀 Quick Start in 5 Minutes

### Prerequisites

Install `uv` for faster package installation:
```bash
pip install uv
```

### Step 1: Install Dependencies (2 minutes)

```bash
# Run the installation script
cd scripts
install.bat
```

This will:
- Create virtual environments for backend and frontend
- Install all Python dependencies using uv (much faster!)
- Install Playwright browsers
- Create directories and .env file

### Step 2: Configure API Keys (1 minute)

Edit `.env` file and add your API key:

```bash
# For Google Gemini (Recommended - Free tier available)
GOOGLE_API_KEY=your_api_key_here

# Get your key at: https://makersuite.google.com/app/apikey
```

**Alternative LLM Options:**
- OpenAI GPT: Add `OPENAI_API_KEY`
- Local models: Set `LLM_PROVIDER=ollama` (requires Ollama installed)

### Step 3: Start Qdrant (30 seconds)

**Option A: Docker (Recommended)**
```bash
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

**Option B: Qdrant Cloud**
1. Sign up at https://cloud.qdrant.io/
2. Create a cluster
3. Update `.env` with your cluster URL and API key

### Step 4: Setup Database (1 minute)

```bash
cd scripts
python setup_qdrant.py
python seed_data.py
```

This creates Qdrant collections and seeds the knowledge base with 20+ curated GenAI topics.

### Step 5: Launch Application (30 seconds)

```bash
cd scripts
run_all.bat
```

This starts:
- **Backend** at http://localhost:8000
- **Frontend** at http://localhost:8501

Your browser will automatically open to the Streamlit interface!

---

## 💬 First Conversation

Try these example queries:

1. **"What is LangChain?"**
2. **"How do I build RAG applications?"**
3. **"Compare GPT-4 vs Gemini vs LLaMA"**
4. **"What are the latest trends in image generation?"**

Aria will ask 2-3 clarifying questions before providing detailed answers with sources!

---

## 🔧 Troubleshooting

### Qdrant Connection Error
```bash
# Check if Qdrant is running
curl http://localhost:6333/collections
```
If not running, start Qdrant (see Step 3)

### Missing API Key
```bash
# Verify .env file has your API key
GOOGLE_API_KEY=your_actual_key_here
```

### Module Not Found
```bash
# Activate virtual environment first
cd backend
.venv\Scripts\activate
uv pip install -r requirements.txt
```

---

## 📚 Next Steps

- **Customize Aria**: Edit `backend/app/pipelines/chat_orchestrator.py` to modify persona
- **Add Knowledge**: Add more documents to `data/seed/` and run `seed_data.py`
- **Configure LLMs**: Change `LLM_PROVIDER` and `LLM_MODEL` in `.env`
- **Deploy**: See `docs/deployment.md` for production deployment

---

## 🎯 Key Features to Try

✅ **Ask broad questions** - Aria will ask clarifying questions  
✅ **Multi-turn conversations** - Context is maintained  
✅ **Source citations** - See where information comes from  
✅ **Non-GenAI detection** - Ask about cooking and see the redirect  
✅ **Clear conversations** - Use sidebar button to start fresh  

---

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review `probelmdescription.md` for system architecture
- Open an issue on GitHub
- Check logs in `logs/aria.log`

---

**Enjoy chatting with Aria! 🤖✨**
