import os
import json
import requests
import uuid
from database.chroma_connection import get_chroma_client

def check_message_toxicity(message):
    """
    Check if a message contains toxic or offensive content
    Returns True if toxic, False otherwise
    
    This implementation uses OpenAI's moderation API, but you could also use:
    - Perspective API from Google
    - A local model with LangChain
    - A custom toxicity detection model
    """
    try:
        # Use OpenAI's moderation API
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            # Fallback to a simple keyword-based check if no API key is available
            return _simple_toxicity_check(message)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "input": message
        }
        
        response = requests.post(
            "https://api.openai.com/v1/moderations",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if the message is flagged
            is_toxic = result["results"][0]["flagged"]
            
            # If toxic, store the report
            if is_toxic:
                _store_toxic_report(message, result["results"][0]["categories"])
            
            return is_toxic
        else:
            # Fallback to simple check if API call fails
            return _simple_toxicity_check(message)
    
    except Exception as e:
        # Fallback to simple check if any error occurs
        return _simple_toxicity_check(message)

def _simple_toxicity_check(message):
    """
    A simple keyword-based toxicity check
    This is a fallback method and not as accurate as using an AI model
    """
    # List of offensive words (this is a very basic list - in a real app, you'd use a more comprehensive list)
    offensive_words = [
        "fuck", "shit", "ass", "bitch", "dick", "pussy", "cunt", "whore", "slut",
        "bastard", "damn", "hell", "asshole", "motherfucker", "bullshit"
    ]
    
    # Check if any offensive word is in the message
    message_lower = message.lower()
    for word in offensive_words:
        if word in message_lower:
            # Store the report
            _store_toxic_report(message, {"profanity": True})
            return True
    
    return False

def _store_toxic_report(message, categories):
    """
    Store a report of a toxic message in the ChromaDB toxic_reports collection
    """
    client = get_chroma_client()
    toxic_reports_collection = client.get_collection("toxic_reports")
    
    # Generate a unique ID for the report
    report_id = str(uuid.uuid4())
    
    # Create report data
    report_data = {
        "message": message,
        "categories": categories,
        "timestamp": str(uuid.uuid1())  # Use timestamp for sorting
    }
    
    # Store the report
    toxic_reports_collection.add(
        ids=[report_id],
        documents=[json.dumps(report_data)],
        metadatas=[{"timestamp": report_data["timestamp"]}]
    )
