import json
import uuid
import datetime
from database.chroma_connection import get_chroma_client

def send_message(sender_email, receiver_email, message):
    """
    Store a chat message in the ChromaDB chats collection
    Returns the message ID
    """
    client = get_chroma_client()
    chats_collection = client.get_collection("chats")
    
    # Generate a unique ID for the message
    message_id = str(uuid.uuid4())
    
    # Create message data
    timestamp = datetime.datetime.now().isoformat()
    message_data = {
        "sender": sender_email,
        "receiver": receiver_email,
        "message": message,
        "timestamp": timestamp
    }
    
    # Store the message
    chats_collection.add(
        ids=[message_id],
        documents=[json.dumps(message_data)],
        metadatas=[{
            "sender": sender_email,
            "receiver": receiver_email,
            "timestamp": timestamp
        }]
    )
    
    return message_id

def get_chat_history(user1_email, user2_email):
    """
    Retrieve chat history between two users from the ChromaDB chats collection
    Returns a list of messages sorted by timestamp
    """
    client = get_chroma_client()
    chats_collection = client.get_collection("chats")
    
    # Query for messages between the two users (in both directions)
    results1 = chats_collection.query(
        query_texts=[""],
        where={
            "$and": [
                {"sender": user1_email},
                {"receiver": user2_email}
            ]
        },
        limit=100
    )
    
    results2 = chats_collection.query(
        query_texts=[""],
        where={
            "$and": [
                {"sender": user2_email},
                {"receiver": user1_email}
            ]
        },
        limit=100
    )
    
    # Combine and parse the messages
    messages = []
    
    if results1["ids"] and len(results1["ids"][0]) > 0:
        for i, msg_id in enumerate(results1["ids"][0]):
            message_data = json.loads(results1["documents"][0][i])
            messages.append(message_data)
    
    if results2["ids"] and len(results2["ids"][0]) > 0:
        for i, msg_id in enumerate(results2["ids"][0]):
            message_data = json.loads(results2["documents"][0][i])
            messages.append(message_data)
    
    # Sort messages by timestamp
    messages.sort(key=lambda x: x["timestamp"])
    
    return messages

def count_user_messages(user_email):
    """
    Count the number of messages sent by a user
    Returns the message count
    """
    client = get_chroma_client()
    chats_collection = client.get_collection("chats")
    
    # Query for messages sent by the user
    results = chats_collection.query(
        query_texts=[""],
        where={"sender": user_email}
    )
    
    if results["ids"] and len(results["ids"][0]) > 0:
        return len(results["ids"][0])
    
    return 0
