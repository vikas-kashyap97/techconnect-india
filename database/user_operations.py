import json
import uuid
from database.chroma_connection import get_chroma_client

def create_user(user_data):
    """
    Create a new user in the ChromaDB users collection
    Returns the user ID
    """
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    
    # Generate a unique ID for the user
    user_id = str(uuid.uuid4())
    
    # Store the user data
    users_collection.add(
        ids=[user_id],
        documents=[json.dumps(user_data)],
        metadatas=[{
            "email": user_data["email"],
            "name": user_data["name"],
            "city": user_data["city"],
            "subscription_status": user_data.get("subscription_status", "free"),
            "message_count": user_data.get("message_count", 0)
        }]
    )
    
    return user_id

def get_user_by_email(email):
    """
    Retrieve a user by email from the ChromaDB users collection
    Returns the user data or None if not found
    """
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    
    # Query for the user by email
    results = users_collection.query(
        query_texts=[""],
        where={"email": email},
        limit=1
    )
    
    if results["ids"] and len(results["ids"][0]) > 0:
        user_id = results["ids"][0][0]
        user_data = json.loads(results["documents"][0][0])
        return user_data
    
    return None

def update_user(email, update_data):
    """
    Update a user's data in the ChromaDB users collection
    Returns True if successful, False otherwise
    """
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    
    # Query for the user by email
    results = users_collection.query(
        query_texts=[""],
        where={"email": email},
        limit=1
    )
    
    if results["ids"] and len(results["ids"][0]) > 0:
        user_id = results["ids"][0][0]
        
        # Get the current user data
        user_data = json.loads(results["documents"][0][0])
        
        # Update the user data
        for key, value in update_data.items():
            user_data[key] = value
        
        # Update the metadata
        metadata = {
            "email": user_data["email"],
            "name": user_data["name"],
            "city": user_data["city"],
            "subscription_status": user_data.get("subscription_status", "free"),
            "message_count": user_data.get("message_count", 0)
        }
        
        # Update the document in ChromaDB
        users_collection.update(
            ids=[user_id],
            documents=[json.dumps(user_data)],
            metadatas=[metadata]
        )
        
        return True
    
    return False

def get_all_users(exclude_email=None):
    """
    Retrieve all users from the ChromaDB users collection
    Optionally exclude a user by email (e.g., the current user)
    Returns a list of user data
    """
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    
    # Get all users
    results = users_collection.get()
    
    users = []
    for i, user_id in enumerate(results["ids"]):
        user_data = json.loads(results["documents"][i])
        
        # Skip the excluded user
        if exclude_email and user_data["email"] == exclude_email:
            continue
        
        users.append(user_data)
    
    return users

def get_users_by_city(city, exclude_email=None):
    """
    Retrieve users from a specific city from the ChromaDB users collection
    Optionally exclude a user by email (e.g., the current user)
    Returns a list of user data
    """
    client = get_chroma_client()
    users_collection = client.get_collection("users")
    
    # Query for users by city
    results = users_collection.query(
        query_texts=[""],
        where={"city": city}
    )
    
    users = []
    for i, user_id in enumerate(results["ids"][0]):
        user_data = json.loads(results["documents"][0][i])
        
        # Skip the excluded user
        if exclude_email and user_data["email"] == exclude_email:
            continue
        
        users.append(user_data)
    
    return users
