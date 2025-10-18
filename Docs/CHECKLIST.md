# 🎯 Aria Chatbot - Setup Checklist

Use this checklist to ensure everything is properly set up.

## ✅ Pre-Installation

- [ ] Python 3.10+ installed
- [ ] Docker installed (for Qdrant) OR Qdrant Cloud account
- [ ] Git installed (optional, for version control)
- [ ] Code editor (VS Code recommended)

---

### ✅ Installation Steps

### 1. Environment Setup
- [ ] Installed uv: `pip install uv`
- [ ] Cloned/downloaded the project
- [ ] Navigated to project directory
- [ ] Ran `scripts\install.bat`
- [ ] Verified no errors during installation
- [ ] Both backend and frontend `.venv` folders created

### 2. Configuration
- [ ] `.env` file created from `.env.example`
- [ ] Added `GOOGLE_API_KEY` to `.env` file
- [ ] (Optional) Configured other LLM providers
- [ ] (Optional) Customized Aria's persona

### 3. Database Setup
- [ ] Started Qdrant (Docker or Cloud)
- [ ] Verified Qdrant accessible at http://localhost:6333
- [ ] Ran `python scripts/setup_qdrant.py`
- [ ] Saw success message with collections created
- [ ] Ran `python scripts/seed_data.py`
- [ ] Saw 20+ points uploaded to knowledge base

### 4. Launch Application
- [ ] Ran `scripts\run_all.bat`
- [ ] Backend started at http://localhost:8000
- [ ] Frontend started at http://localhost:8501
- [ ] Browser opened automatically to Streamlit

---

## ✅ Verification Tests

### Backend Tests
- [ ] Visit http://localhost:8000 → See {"status":"healthy"}
- [ ] Visit http://localhost:8000/docs → See API documentation
- [ ] Visit http://localhost:8000/persona → See Aria's details

### Frontend Tests
- [ ] Streamlit UI loads without errors
- [ ] Sidebar shows Aria's persona information
- [ ] Chat input box is visible and active

### First Conversation
- [ ] Sent first message "Hello"
- [ ] Received Aria's introduction
- [ ] Saw her mention her name "Aria Voss"
- [ ] Asked a GenAI question
- [ ] Received a response with sources

### Feature Tests
- [ ] **Clarifying Questions**: Ask "What's the best framework?" → Aria asks 2-3 clarifying questions
- [ ] **GenAI Detection**: Ask about cooking → Aria politely redirects
- [ ] **Sources**: Responses show source citations
- [ ] **Confidence**: Responses show confidence scores
- [ ] **Memory**: Follow-up questions maintain context
- [ ] **Clear**: Sidebar "Clear Conversation" button works

---

## ✅ Advanced Checks

### Database
- [ ] Qdrant dashboard accessible (if using Docker)
- [ ] Collections have expected point counts
- [ ] Can search collections manually

### Logging
- [ ] `logs/aria.log` file exists (after first request)
- [ ] Log entries are readable
- [ ] No critical errors in logs

### Testing
- [ ] Ran `scripts\run_tests.bat`
- [ ] All tests passed
- [ ] (Optional) Coverage report generated

---

## ✅ Troubleshooting Completed

If you encountered issues, mark what you fixed:

- [ ] Fixed Qdrant connection issues
- [ ] Fixed API key problems
- [ ] Fixed module import errors
- [ ] Fixed port conflicts
- [ ] Fixed virtual environment issues
- [ ] Installed uv for faster package management

---

## ✅ Optional Enhancements

Mark any customizations you made:

- [ ] Changed Aria's personality/persona
- [ ] Added custom knowledge to seed data
- [ ] Configured different LLM provider
- [ ] Adjusted temperature/parameters
- [ ] Modified UI styling
- [ ] Added authentication
- [ ] Set up monitoring

---

## ✅ Deployment (If Applicable)

- [ ] Configured for production environment
- [ ] Set production environment variables
- [ ] Enabled CORS for production domain
- [ ] Set up SSL/HTTPS
- [ ] Configured logging for production
- [ ] Set up monitoring/alerting
- [ ] Deployed backend to cloud
- [ ] Deployed frontend to cloud
- [ ] Verified production deployment works

---

## 📊 Final Status

**Installation Complete:** [ ] Yes [ ] No  
**Backend Working:** [ ] Yes [ ] No  
**Frontend Working:** [ ] Yes [ ] No  
**Database Seeded:** [ ] Yes [ ] No  
**First Conversation:** [ ] Yes [ ] No  

**Overall Status:** [ ] 🎉 Ready to Use!

---

## 📞 Getting Help

If any checkbox is unchecked:

1. **Check Logs**: `logs/aria.log` for backend errors
2. **Check Console**: Terminal output for error messages
3. **Check Documentation**: README.md, QUICKSTART.md
4. **Check Environment**: Verify .env file has correct values
5. **Check Services**: Ensure Qdrant is running

Common Solutions:
- Qdrant not running → `docker ps` to check
- API key error → Verify in .env file
- Module errors → Reinstall with `uv pip install -r requirements.txt`
- Port conflicts → Change ports in .env
- uv not installed → Run `pip install uv`

---

## 🎯 Success Criteria

You're ready when:
✅ You can chat with Aria about GenAI topics  
✅ Aria asks clarifying questions  
✅ Sources are shown for responses  
✅ Conversation context is maintained  
✅ Non-GenAI topics are redirected  

---

**Date Completed:** __________  
**Time Taken:** __________  
**Notes:** 
_______________________________________
_______________________________________
_______________________________________
