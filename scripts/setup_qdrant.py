"""
Setup Qdrant Collections for Aria Chatbot
Initializes vector database collections for knowledge base and conversations
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
KNOWLEDGE_COLLECTION = os.getenv("QDRANT_COLLECTION_NAME", "aria_genai_knowledge")
MEMORY_COLLECTION = os.getenv("QDRANT_MEMORY_COLLECTION", "aria_conversations")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))


def setup_qdrant():
    """Initialize Qdrant collections"""
    try:
        # Connect to Qdrant
        logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # Check connection
        collections = client.get_collections()
        logger.info(f"Connected successfully. Existing collections: {len(collections.collections)}")
        
        # Create knowledge collection
        logger.info(f"Creating/updating knowledge collection: {KNOWLEDGE_COLLECTION}")
        try:
            client.delete_collection(collection_name=KNOWLEDGE_COLLECTION)
            logger.info(f"Deleted existing collection: {KNOWLEDGE_COLLECTION}")
        except Exception:
            pass
        
        client.create_collection(
            collection_name=KNOWLEDGE_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
        logger.info(f"✓ Created knowledge collection: {KNOWLEDGE_COLLECTION}")
        
        # Create memory/conversation collection
        logger.info(f"Creating/updating memory collection: {MEMORY_COLLECTION}")
        try:
            client.delete_collection(collection_name=MEMORY_COLLECTION)
            logger.info(f"Deleted existing collection: {MEMORY_COLLECTION}")
        except Exception:
            pass
        
        client.create_collection(
            collection_name=MEMORY_COLLECTION,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
        logger.info(f"✓ Created memory collection: {MEMORY_COLLECTION}")
        
        # Verify collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        logger.info("\n" + "="*50)
        logger.info("Qdrant Setup Complete!")
        logger.info("="*50)
        logger.info(f"Collections created:")
        for name in collection_names:
            info = client.get_collection(name)
            logger.info(f"  • {name}: {info.points_count} points")
        logger.info("="*50)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup Qdrant: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("Starting Qdrant setup for Aria chatbot...")
    success = setup_qdrant()
    
    if success:
        logger.info("\n✓ Setup completed successfully!")
        logger.info("Next steps:")
        logger.info("  1. Run seed_data.py to populate the knowledge base")
        logger.info("  2. Start the backend: python backend/main.py")
        logger.info("  3. Start the frontend: streamlit run frontend/app.py")
    else:
        logger.error("\n✗ Setup failed. Please check the logs above.")
        sys.exit(1)
