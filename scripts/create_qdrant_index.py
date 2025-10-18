#!/usr/bin/env python3
"""
Script to create field indexes in Qdrant collections.
Run this once to fix the 400 error for session_id searches.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.config import settings
from qdrant_client import QdrantClient

def create_session_id_index():
    """Create field index for session_id in aria_conversations collection."""
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=30
    )

    try:
        # Create field index for session_id
        client.create_payload_index(
            collection_name="aria_conversations",
            field_name="session_id",
            field_type="keyword"  # Use keyword for string/uuid filtering
        )
        print("✓ Successfully created field index for 'session_id' in 'aria_conversations' collection")
    except Exception as e:
        print(f"✗ Failed to create index: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Creating Qdrant field index for session_id...")
    success = create_session_id_index()
    if success:
        print("Index creation complete. Memory searches should now work without 400 errors.")
    else:
        print("Index creation failed. Check your Qdrant connection and try again.")