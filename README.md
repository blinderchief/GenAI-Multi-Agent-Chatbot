# Aria - Generative AI Chatbot

A sophisticated human-like chatbot powered by LLMs with multi-agent architecture, specializing in Generative AI expertise.

## 🤖 About Aria

**Aria Voss** is a 28-year-old Research Analyst specializing in Generative AI trends. With a master's degree in Computer Science from MIT, Aria provides expert guidance on:

- Machine Learning & Deep Learning
- Natural Language Processing
- Computer Vision & Image Generation
- Speech & Audio AI
- Multimodal AI Systems
- GenAI Tools & Frameworks (LangChain, LangGraph, etc.)
- Research Papers & Industry Trends
- AI Libraries (PyTorch, TensorFlow, Hugging Face)
- Large Language Models (GPT, LLaMA, Mistral, Gemini)
- Diffusion Models & Image Generation
- RAG & Vector Databases

## 🏗️ Architecture

### Multi-Agent System

Aria uses a sophisticated multi-level agent architecture:

1. **Retrieval Agent** - Queries Qdrant vector database for domain-specific knowledge
2. **Web Scraper Agent** - Fetches latest updates, papers, and trends from the web
3. **Reasoning Agent** - Synthesizes information using LLMs (Gemini/GPT/LLaMA)
4. **Memory Agent** - Maintains conversation context and user preferences
5. **Evaluation Agent** - Validates responses for accuracy and relevance

### Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Vector Database**: Qdrant
- **LLMs**: Google Gemini, GPT-4, LLaMA 3, Mistral
- **Agent Orchestration**: LangChain, LangGraph
- **Web Scraping**: Playwright, BeautifulSoup
- **Evaluation**: Ragas, LangSmith

## 📁 Project Structure

```
GenAI_MultiAgent_Chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── models.py              # Pydantic models
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── retrieval_agent.py
│   │   │   ├── web_scraper_agent.py
│   │   │   ├── reasoning_agent.py
│   │   │   ├── memory_agent.py
│   │   │   └── evaluation_agent.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_service.py
│   │   │   ├── embedding_service.py
│   │   │   └── qdrant_service.py
│   │   └── pipelines/
│   │       ├── __init__.py
│   │       └── chat_orchestrator.py
│   ├── main.py                    # FastAPI entry point
│   └── requirements.txt
├── frontend/
│   ├── app.py                     # Streamlit app
│   └── requirements.txt
├── data/
│   └── seed/                      # Initial knowledge base
├── scripts/
│   ├── setup_qdrant.py           # Initialize Qdrant
│   ├── seed_data.py              # Seed knowledge base
│   └── run_all.bat               # Start all services
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- uv (fast Python package installer) - Install: `pip install uv`
- Qdrant (local or cloud)
- Google Gemini API key (or OpenAI API key)

### 1. Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd GenAI_MultiAgent_Chatbot

# Copy environment file
copy .env.example .env

# Edit .env and add your API keys
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
uv venv
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. Start Qdrant

**Option A: Docker** (Recommended)
```bash
docker run -p 6333:6333 -p 6334:6334 -v "%cd%\qdrant_storage:/qdrant/storage" qdrant/qdrant
```

**Option B: Cloud**
- Sign up at https://cloud.qdrant.io/
- Update QDRANT_URL and QDRANT_API_KEY in .env

### 4. Initialize Database

```bash
cd scripts
python setup_qdrant.py
python seed_data.py
```

### 5. Run the Application

**Start Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

Backend will run at: http://localhost:8000

**Start Frontend:**
```bash
cd frontend
venv\Scripts\activate
streamlit run app.py
```

Frontend will run at: http://localhost:8501

### 6. Use the Chatbot

1. Open http://localhost:8501 in your browser
2. Start chatting with Aria about Generative AI topics!

**Note:** `uv` is much faster than `pip` for package installation. If you don't have it, install with: `pip install uv`

## 💡 Features

### Core Features

✅ **Human-like Persona** - Aria presents as a real person with background and personality  
✅ **Cross-Questioning** - Asks 2-3 clarifying questions before answering  
✅ **Multi-Agent Architecture** - Coordinated agents for retrieval, reasoning, memory, and evaluation  
✅ **GenAI Specialization** - Deep knowledge of Generative AI topics  
✅ **Context-Aware** - Maintains conversation history and user preferences  
✅ **Source Citations** - Provides sources for all information  
✅ **Hallucination Detection** - Validates responses for accuracy  

### Optimization Features

✅ **Cost Optimization** - Uses smaller LLMs for most tasks, GPT-4 only when needed  
✅ **Prompt Compression** - Reduces token usage  
✅ **History Summarization** - Maintains context with minimal tokens  
✅ **Hybrid Retrieval** - Vector + keyword search to reduce LLM calls  
✅ **Caching** - Stores frequent queries  

## 🔧 Configuration

Edit `.env` file to customize:

- **LLM Provider**: Choose between Google Gemini, OpenAI, or local models
- **Temperature**: Control response creativity (0.0 - 1.0)
- **Retrieval Settings**: Number of documents to retrieve
- **Memory Settings**: Conversation history length
- **Web Scraping**: Enable/disable web search

## 📊 API Endpoints

### POST /chat
Send a message to Aria
```json
{
  "message": "What are the latest trends in text-to-image models?",
  "session_id": "optional-session-id"
}
```

### GET /conversation/{session_id}
Retrieve conversation history

### DELETE /conversation/{session_id}
Clear conversation history

### GET /persona
Get Aria's persona information

### GET /health
Health check

## 🧪 Testing

```bash
# Run tests
cd backend
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📝 Example Conversations

**User**: "What are the best frameworks for building AI agents?"

**Aria**: "Before I answer, let me clarify a few things:
1. Are you looking for frameworks for autonomous AI agents or conversational agents?
2. Do you prefer Python-based solutions or are you open to other languages?
3. Is this for production use or experimentation?"

**User**: "Python-based frameworks for autonomous agents in production."

**Aria**: "Great! For production-grade autonomous AI agents in Python, I'd recommend:

1. **LangGraph** - Built on LangChain, excellent for complex agent workflows with state management...
2. **CrewAI** - Specialized for multi-agent collaboration...
3. **AutoGPT/AutoGen** - For highly autonomous agents...

[Detailed explanation with sources]"

## 🛠️ Troubleshooting

### Qdrant Connection Error
- Ensure Qdrant is running on port 6333
- Check QDRANT_URL in .env file

### LLM API Error
- Verify API keys in .env file
- Check API quota/rate limits

### Module Import Error
- Ensure virtual environment is activated
- Reinstall requirements: `uv pip install -r requirements.txt`

## 📚 Documentation

- [Detailed Architecture](docs/architecture.md)
- [Agent Design](docs/agents.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- LangChain & LangGraph teams
- Qdrant for vector search
- Google Gemini & OpenAI for LLMs
- Streamlit for the amazing UI framework

---

**Built with ❤️ for the GenAI community**

For questions or support, please open an issue on GitHub.
