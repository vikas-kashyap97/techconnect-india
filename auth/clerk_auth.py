import os
import requests
import json
import streamlit as st
from database.user_operations import get_user_by_email

def get_user_token():
    """
    Get the user token from the Clerk session
    This is a simplified implementation for demo purposes
    In a real app, you'd use Clerk's SDK to verify the session token
    """
    # Check for token in query parameters
    params = st.query_params
    if 'clerk_token' in params:
        return params['clerk_token'][0]
    
    # Check for token in session state
    return st.session_state.get('clerk_token')

def verify_session(token):
    """
    Verify a Clerk session token
    Returns True if valid, False otherwise
    """
    if not token:
        return False
    
    try:
        # Get Clerk API key from environment variables
        api_key = os.getenv("CLERK_SECRET_KEY")
        
        if not api_key:
            # For demo purposes, assume token is valid
            return True
        
        # Verify token with Clerk API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            "https://api.clerk.dev/v1/sessions/verify",
            headers=headers,
            params={"session_token": token}
        )
        
        return response.status_code == 200
    
    except Exception as e:
        st.error(f"Error verifying session: {str(e)}")
        return False

def get_user_data(token):
    """
    Get user data from Clerk using the session token
    Returns user data or None if error
    """
    if not token:
        return None
    
    try:
        # Get Clerk API key from environment variables
        api_key = os.getenv("CLERK_SECRET_KEY")
        
        if not api_key:
            # For demo purposes, return dummy data
            return {
                "id": "user_123",
                "email": "demo@example.com",
                "name": "Demo User",
                "profile_image": "/placeholder.svg?height=200&width=200"
            }
        
        # Get user data from Clerk API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # First, get the user ID from the session
        session_response = requests.get(
            "https://api.clerk.dev/v1/sessions/verify",
            headers=headers,
            params={"session_token": token}
        )
        
        if session_response.status_code != 200:
            return None
        
        session_data = session_response.json()
        user_id = session_data.get("data", {}).get("user_id")
        
        if not user_id:
            return None
        
        # Then, get the user data
        user_response = requests.get(
            f"https://api.clerk.dev/v1/users/{user_id}",
            headers=headers
        )
        
        if user_response.status_code != 200:
            return None
        
        user_data = user_response.json()
        
        # Extract relevant information
        email_addresses = user_data.get("email_addresses", [])
        primary_email = next((email.get("email_address") for email in email_addresses if email.get("id") == user_data.get("primary_email_address_id")), None)
        
        return {
            "id": user_id,
            "email": primary_email,
            "name": f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
            "profile_image": user_data.get("profile_image_url", "/placeholder.svg?height=200&width=200")
        }
    
    except Exception as e:
        st.error(f"Error getting user data: {str(e)}")
        return None
