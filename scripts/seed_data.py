"""
Seed Qdrant with GenAI Knowledge Base
Populates the knowledge collection with curated GenAI information
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
import uuid
from datetime import datetime

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
KNOWLEDGE_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "aria_genai_knowledge")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


# GenAI Knowledge Base
GENAI_KNOWLEDGE = [
    {
        "title": "What is LangChain?",
        "content": "LangChain is a framework for developing applications powered by language models. It enables applications that are context-aware and can reason. LangChain provides modules for models, prompts, memory, indexes, chains, and agents. It's widely used for building chatbots, question answering systems, and complex AI agents.",
        "category": "frameworks",
        "tags": ["langchain", "framework", "llm", "agents"],
        "url": "https://python.langchain.com/"
    },
    {
        "title": "What is LangGraph?",
        "content": "LangGraph is a library for building stateful, multi-actor applications with LLMs, built on top of LangChain. It extends LangChain's expression language with the ability to coordinate multiple chains (or actors) across multiple steps of computation in a cyclic manner. LangGraph is ideal for building complex agent systems with state management.",
        "category": "frameworks",
        "tags": ["langgraph", "langchain", "agents", "stateful"],
        "url": "https://langchain-ai.github.io/langgraph/"
    },
    {
        "title": "What is RAG (Retrieval Augmented Generation)?",
        "content": "RAG is a technique that combines retrieval of relevant documents with text generation. It works by first retrieving relevant documents from a knowledge base using vector similarity search, then using those documents as context for an LLM to generate a response. RAG reduces hallucinations and allows LLMs to access up-to-date information without retraining.",
        "category": "techniques",
        "tags": ["rag", "retrieval", "generation", "vector search"],
        "url": "https://arxiv.org/abs/2005.11401"
    },
    {
        "title": "What is Qdrant?",
        "content": "Qdrant is a vector database optimized for similarity search and vector embeddings. It's written in Rust and provides high performance, scalability, and rich filtering capabilities. Qdrant is commonly used in RAG systems, semantic search, and recommendation engines. It supports both in-memory and disk-based storage.",
        "category": "vector_databases",
        "tags": ["qdrant", "vector database", "embeddings", "similarity search"],
        "url": "https://qdrant.tech/"
    },
    {
        "title": "What are Transformers?",
        "content": "Transformers are a neural network architecture introduced in the 'Attention is All You Need' paper. They use self-attention mechanisms to process sequential data in parallel, unlike RNNs. Transformers are the foundation of modern LLMs like GPT, BERT, and T5. The Hugging Face Transformers library provides thousands of pretrained models.",
        "category": "architectures",
        "tags": ["transformers", "attention", "neural networks", "llm"],
        "url": "https://arxiv.org/abs/1706.03762"
    },
    {
        "title": "What is Stable Diffusion?",
        "content": "Stable Diffusion is a latent text-to-image diffusion model capable of generating photo-realistic images from text descriptions. It uses a latent diffusion process, working in compressed latent space rather than pixel space, making it more efficient. Stable Diffusion is open-source and can run on consumer GPUs.",
        "category": "image_generation",
        "tags": ["stable diffusion", "diffusion models", "text-to-image", "generative ai"],
        "url": "https://stability.ai/stable-diffusion"
    },
    {
        "title": "What is GPT (Generative Pre-trained Transformer)?",
        "content": "GPT is a series of large language models developed by OpenAI. GPT models are trained on vast amounts of text data and can generate human-like text, answer questions, write code, and more. GPT-4 is the latest version with multimodal capabilities. GPT models use transformer architecture and are trained using next-token prediction.",
        "category": "llms",
        "tags": ["gpt", "openai", "llm", "language model"],
        "url": "https://openai.com/gpt-4"
    },
    {
        "title": "What is LLaMA?",
        "content": "LLaMA (Large Language Model Meta AI) is a family of open-source large language models developed by Meta. LLaMA 2 and LLaMA 3 are available for research and commercial use. These models range from 7B to 70B parameters and are designed to be efficient and performant. LLaMA models can be fine-tuned for specific tasks.",
        "category": "llms",
        "tags": ["llama", "meta", "open source", "llm"],
        "url": "https://ai.meta.com/llama/"
    },
    {
        "title": "What is Google Gemini?",
        "content": "Google Gemini is a multimodal AI model developed by Google DeepMind. It can understand and generate text, images, audio, and video. Gemini comes in three sizes: Ultra, Pro, and Nano. Gemini Pro is available through Google AI Studio and the Gemini API. It excels at reasoning, coding, and multimodal tasks.",
        "category": "llms",
        "tags": ["gemini", "google", "multimodal", "llm"],
        "url": "https://deepmind.google/technologies/gemini/"
    },
    {
        "title": "What is Mistral AI?",
        "content": "Mistral AI is a company that develops open-source large language models. Their flagship models include Mistral 7B, Mixtral 8x7B, and Mistral Large. These models are known for excellent performance-to-size ratios and are available under permissive licenses. Mistral models use mixture-of-experts architecture for efficiency.",
        "category": "llms",
        "tags": ["mistral", "open source", "llm", "mixture of experts"],
        "url": "https://mistral.ai/"
    },
    {
        "title": "What is Fine-tuning?",
        "content": "Fine-tuning is the process of adapting a pre-trained model to a specific task or domain by training it on a smaller, task-specific dataset. Fine-tuning is more efficient than training from scratch and produces better results than zero-shot learning. Techniques include full fine-tuning, LoRA, QLoRA, and adapter tuning.",
        "category": "techniques",
        "tags": ["fine-tuning", "training", "transfer learning", "lora"],
        "url": "https://huggingface.co/docs/transformers/training"
    },
    {
        "title": "What is Prompt Engineering?",
        "content": "Prompt engineering is the practice of designing effective prompts to get desired outputs from language models. Techniques include few-shot learning, chain-of-thought prompting, role-playing, and structured prompts. Good prompts provide clear instructions, examples, and context. Prompt engineering is crucial for maximizing LLM performance.",
        "category": "techniques",
        "tags": ["prompt engineering", "prompting", "llm", "few-shot"],
        "url": "https://www.promptingguide.ai/"
    },
    {
        "title": "What are Embeddings?",
        "content": "Embeddings are dense vector representations of text, images, or other data that capture semantic meaning. Similar items have similar embeddings in vector space. Embeddings are used for semantic search, clustering, classification, and recommendations. Popular embedding models include sentence-transformers, OpenAI embeddings, and Cohere embeddings.",
        "category": "techniques",
        "tags": ["embeddings", "vectors", "semantic search", "representation learning"],
        "url": "https://www.sbert.net/"
    },
    {
        "title": "What is Hugging Face?",
        "content": "Hugging Face is a platform and community for machine learning, particularly NLP. It provides the Transformers library with thousands of pre-trained models, datasets, and model cards. Hugging Face Hub hosts models, datasets, and spaces (ML applications). It's the go-to platform for accessing and sharing AI models.",
        "category": "platforms",
        "tags": ["hugging face", "transformers", "model hub", "nlp"],
        "url": "https://huggingface.co/"
    },
    {
        "title": "What is PyTorch?",
        "content": "PyTorch is an open-source machine learning framework developed by Meta. It provides tensor computation with GPU acceleration and a neural network library. PyTorch is known for its dynamic computational graph, making it intuitive and flexible. It's widely used in research and production for deep learning applications.",
        "category": "frameworks",
        "tags": ["pytorch", "deep learning", "framework", "neural networks"],
        "url": "https://pytorch.org/"
    },
    {
        "title": "What is Agent Architecture?",
        "content": "Agent architecture refers to the design of AI systems that can take actions to achieve goals. Common patterns include ReAct (Reasoning + Acting), Plan-and-Execute, and Reflexion. Agents typically have access to tools, memory, and planning capabilities. Multi-agent systems coordinate multiple specialized agents for complex tasks.",
        "category": "architectures",
        "tags": ["agents", "architecture", "react", "planning"],
        "url": "https://lilianweng.github.io/posts/2023-06-23-agent/"
    },
    {
        "title": "What is CrewAI?",
        "content": "CrewAI is a framework for orchestrating role-playing autonomous AI agents. Agents in CrewAI have roles, goals, and backstories, and can collaborate on tasks. It's built on LangChain and provides a high-level API for multi-agent systems. CrewAI is ideal for complex workflows requiring specialization and collaboration.",
        "category": "frameworks",
        "tags": ["crewai", "agents", "multi-agent", "orchestration"],
        "url": "https://www.crewai.com/"
    },
    {
        "title": "What is LlamaIndex?",
        "content": "LlamaIndex (formerly GPT Index) is a data framework for connecting custom data sources to large language models. It provides data connectors, indexing strategies, and retrieval mechanisms. LlamaIndex excels at building RAG applications and is particularly good at handling structured and unstructured data sources.",
        "category": "frameworks",
        "tags": ["llamaindex", "data framework", "rag", "retrieval"],
        "url": "https://www.llamaindex.ai/"
    },
    {
        "title": "What is Diffusion Model?",
        "content": "Diffusion models are generative models that learn to denoise data by reversing a gradual noising process. They work by adding noise to data in steps, then learning to reverse this process. Diffusion models power image generation systems like Stable Diffusion, DALL-E 2, and Midjourney. They produce high-quality, diverse outputs.",
        "category": "architectures",
        "tags": ["diffusion", "generative models", "image generation", "denoising"],
        "url": "https://arxiv.org/abs/2006.11239"
    },
    {
        "title": "What is Multimodal AI?",
        "content": "Multimodal AI refers to systems that can process and generate multiple types of data (text, images, audio, video). Examples include GPT-4V, Gemini, and CLIP. Multimodal models can answer questions about images, generate images from text, and more. They use techniques like cross-attention and contrastive learning.",
        "category": "techniques",
        "tags": ["multimodal", "vision-language", "clip", "cross-modal"],
        "url": "https://openai.com/research/clip"
    }
]


def seed_knowledge_base():
    """Seed Qdrant with GenAI knowledge"""
    try:
        # Connect to Qdrant
        logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Load embedding model
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Prepare points
        logger.info("Generating embeddings for knowledge base...")
        points = []
        
        for idx, item in enumerate(GENAI_KNOWLEDGE):
            # Create text for embedding (title + content)
            text = f"{item['title']} {item['content']}"
            
            # Generate embedding
            embedding = model.encode(text).tolist()
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "title": item["title"],
                    "content": item["content"],
                    "category": item["category"],
                    "tags": item["tags"],
                    "url": item["url"],
                    "created_at": datetime.utcnow().isoformat(),
                    "source_type": "curated"
                }
            )
            points.append(point)
            
            logger.info(f"  [{idx+1}/{len(GENAI_KNOWLEDGE)}] {item['title']}")
        
        # Upload to Qdrant
        logger.info(f"Uploading {len(points)} points to Qdrant...")
        client.upsert(
            collection_name=KNOWLEDGE_COLLECTION,
            points=points
        )
        
        # Verify
        collection_info = client.get_collection(KNOWLEDGE_COLLECTION)
        
        logger.info("\n" + "="*50)
        logger.info("Knowledge Base Seeding Complete!")
        logger.info("="*50)
        logger.info(f"Collection: {KNOWLEDGE_COLLECTION}")
        logger.info(f"Points: {collection_info.points_count}")
        logger.info(f"Vector dimension: {collection_info.config.params.vectors.size}")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to seed knowledge base: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Starting knowledge base seeding for Aria chatbot...")
    success = seed_knowledge_base()
    
    if success:
        logger.info("\n✓ Seeding completed successfully!")
        logger.info("Next steps:")
        logger.info("  1. Start the backend: python backend/main.py")
        logger.info("  2. Start the frontend: streamlit run frontend/app.py")
    else:
        logger.error("\n✗ Seeding failed. Please check the logs above.")
        sys.exit(1)
