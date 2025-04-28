import os
import chromadb
from chromadb.config import Settings

def get_chroma_client():
    """
    Initialize and return a ChromaDB client using the new configuration approach
    """
    # Get the persistence directory from environment variables or use a default
    persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # Create the client with persistence using the new configuration approach
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Ensure collections exist
    _ensure_collections(client)
    
    return client

def _ensure_collections(client):
    """
    Ensure that all required collections exist in ChromaDB
    """
    # Get existing collections
    existing_collections = [col.name for col in client.list_collections()]
    
    # Create users collection if it doesn't exist
    if "users" not in existing_collections:
        client.create_collection(
            name="users",
            metadata={"hnsw:space": "cosine"}
        )
    
    # Create chats collection if it doesn't exist
    if "chats" not in existing_collections:
        client.create_collection(
            name="chats",
            metadata={"hnsw:space": "cosine"}
        )
    
    # Create toxic_reports collection if it doesn't exist
    if "toxic_reports" not in existing_collections:
        client.create_collection(
            name="toxic_reports",
            metadata={"hnsw:space": "cosine"}
        )
    
    return client
