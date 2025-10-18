"""
Streamlit Frontend for Suyash - Generative AI Chatbot
Interactive UI for chatting with Suyash
"""
import streamlit as st
import requests
from datetime import datetime
import uuid
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Suyash - GenAI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
        color: #0A0A0A;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #43A047;
        color: #111111;
    }
    /* Ensure nested text (strong, links) inherit readable color */
    .assistant-message a, .assistant-message strong, .assistant-message span,
    .user-message a, .user-message strong, .user-message span {
        color: inherit !important;
    }
    .source-card {
        background-color: #FFF3E0; /* light theme default */
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin: 0.5rem 0;
        border-left: 3px solid #FF9800;
        color: #1a1a1a; /* ensure readable text on light bg */
    }
    .source-card .source-title {
        font-weight: 700;
        color: #0d0d0d;
        margin-bottom: 0.25rem;
        display: block;
    }
    .source-card .source-meta {
        color: #424242;
        font-size: 0.9rem;
        margin-bottom: 0.25rem;
        display: block;
    }
    .source-card a {
        color: #0D47A1 !important;
        text-decoration: underline;
    }
    /* Dark theme adjustments */
    @media (prefers-color-scheme: dark) {
        .assistant-message { background-color: #1f1f1f; color: #e8e8e8; }
        .user-message { background-color: #0f2a43; color: #e6f1ff; }
        .source-card {
            background-color: #262626; /* darker card for dark theme */
            border-left-color: #FFB74D;
            color: #efefef; /* force light text on dark bg */
        }
        .source-card .source-title { color: #ffffff; }
        .source-card .source-meta { color: #cfcfcf; }
        .source-card a { color: #90CAF9 !important; }
    }
    .metric-card {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False


def get_persona():
    """Fetch Suyash's persona from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/persona")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Failed to fetch persona: {str(e)}")
    return None


def send_message(message: str):
    """Send message to API and get response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Failed to send message: {str(e)}")
        return None


def clear_conversation():
    """Clear current conversation"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/conversation/{st.session_state.session_id}"
        )
        
        if response.status_code == 200:
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.conversation_started = False
            st.success("Conversation cleared!")
            st.rerun()
        else:
            st.error("Failed to clear conversation")
            
    except Exception as e:
        st.error(f"Error clearing conversation: {str(e)}")


# Sidebar
with st.sidebar:
    st.markdown("### 🤖 About Suyash")
    
    persona = get_persona()
    if persona:
        st.markdown(f"**Name:** {persona['name']}")
        st.markdown(f"**Role:** {persona['role']}")
        st.markdown(f"**Background:** {persona['background']}")
        st.markdown("**Interests:**")
        for interest in persona['interests']:
            st.markdown(f"- {interest}")
        st.markdown(f"**Style:** {persona['style']}")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Session Info")
    st.markdown(f"**Session ID:**  \n`{st.session_state.session_id[:8]}...`")
    st.markdown(f"**Messages:** {len(st.session_state.messages)}")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        clear_conversation()
    
    st.markdown("---")
    
    st.markdown("### 📚 Topics I Cover")
    st.markdown("""
    - Machine Learning & Deep Learning
    - Natural Language Processing
    - Computer Vision
    - Speech & Audio AI
    - Multimodal AI
    - GenAI Tools & Frameworks
    - Research Papers & Trends
    - AI Libraries (PyTorch, TensorFlow, etc.)
    - LLMs (GPT, LLaMA, Mistral, etc.)
    - Diffusion Models
    - RAG & Vector Databases
    """)

# Main content
st.markdown('<p class="main-header">🤖 Suyash - Your GenAI Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Research Analyst specializing in Generative AI</p>', unsafe_allow_html=True)

# Display chat messages
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        # Show welcome message
        st.info("""
    👋 **Welcome!** I'm Suyash, your GenAI research companion.  
        
        I can help you with:
        - Understanding GenAI tools, frameworks, and models
        - Exploring the latest research trends
        - Comparing different AI libraries and approaches
        - Practical implementation guidance
        - And much more related to Generative AI!
        
        Ask me anything about Generative AI to get started.
        """)
    else:
        # Display conversation history
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user-message">'
                    f'<strong>You:</strong><br>{msg["content"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant-message">'
                    f'<strong>Suyash:</strong><br>{msg["content"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                # Show sources if available
                if "sources" in msg and msg["sources"]:
                    with st.expander(f"📚 Sources ({len(msg['sources'])})"):
                        for idx, source in enumerate(msg["sources"], 1):
                            title = source.get("title", "Unknown")
                            st.markdown(
                                f'<div class="source-card">'
                                f'<span class="source-title">{idx}. {title}</span>'
                                f'<span class="source-meta">Type: {source.get("type", "N/A")} | '
                                f'Relevance: {source.get("relevance", 0):.2f}</span>'
                                f'<a href="{source.get("url", "#")}" target="_blank">View Source</a>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                
                # Show metadata if available
                if "metadata" in msg and msg["metadata"]:
                    with st.expander("ℹ️ Response Details"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Confidence", f"{msg.get('confidence', 0):.2%}")
                        with col2:
                            st.metric("Retrieval Sources", msg["metadata"].get("retrieval_sources", 0))
                        with col3:
                            st.metric("Web Sources", msg["metadata"].get("web_sources", 0))

# Chat input
st.markdown("---")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Your message:",
            placeholder="Ask me anything about Generative AI...",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 📤", use_container_width=True)

if submit_button and user_input:
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show loading spinner
    with st.spinner("Suyash is thinking..."):
        # Send to API
        response_data = send_message(user_input)
        
        if response_data:
            # Add assistant response to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data["response"],
                "confidence": response_data.get("confidence", 0),
                "sources": response_data.get("sources", []),
                "metadata": response_data.get("metadata", {})
            })
            
            st.session_state.conversation_started = True
    
    # Rerun to update chat display
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #999;">Built with ❤️ using FastAPI, Streamlit, and Multi-Agent AI | '
    'Powered by LangChain, Qdrant, and LLMs</p>',
    unsafe_allow_html=True
)
