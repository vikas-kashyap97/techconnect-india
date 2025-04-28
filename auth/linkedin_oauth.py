import os
import requests
import json
from urllib.parse import urlencode
import streamlit as st
from database.user_operations import get_user_by_email

def initialize_linkedin_auth():
    """
    Initialize LinkedIn OAuth flow and return the authorization URL
    """
    # LinkedIn OAuth configuration
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
    
    # Define the authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "r_liteprofile r_emailaddress",
        "state": "random_state_string"  # In production, use a secure random string
    }
    
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
    return auth_url

def process_linkedin_callback(code):
    """
    Process the LinkedIn callback code and retrieve user information
    """
    try:
        # Exchange code for access token
        client_id = os.getenv("LINKEDIN_CLIENT_ID")
        client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_payload)
        token_data = token_response.json()
        
        if "access_token" not in token_data:
            return None
        
        access_token = token_data["access_token"]
        
        # Get user profile
        profile_url = "https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        profile_response = requests.get(profile_url, headers=headers)
        profile_data = profile_response.json()
        
        # Get user email
        email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        email_response = requests.get(email_url, headers=headers)
        email_data = email_response.json()
        
        # Extract relevant information
        first_name = profile_data.get("localizedFirstName", "")
        last_name = profile_data.get("localizedLastName", "")
        full_name = f"{first_name} {last_name}"
        
        email = None
        if "elements" in email_data and len(email_data["elements"]) > 0:
            email = email_data["elements"][0]["handle~"]["emailAddress"]
        
        # Get additional profile information (position, company, etc.)
        # Note: In a real implementation, you would need to use LinkedIn's Profile API
        # This is simplified for the demo
        position_url = "https://api.linkedin.com/v2/positions"
        position_response = requests.get(position_url, headers=headers, params={"q": "members", "projection": "(elements*)"})
        
        # Check if the user is in the tech industry
        # This is a simplified check - in a real app, you'd use more sophisticated verification
        is_tech_professional = verify_tech_background(profile_data, position_response.json())
        
        if not is_tech_professional:
            return None
        
        # For demo purposes, we'll assume the user is in the tech industry
        # and set a default city (in a real app, you'd get this from LinkedIn or ask the user)
        user_data = {
            "name": full_name,
            "email": email,
            "city": "Bangalore",  # Default city, would be retrieved from LinkedIn or user input
            "skills": ["Python", "JavaScript", "React"],  # Default skills, would be retrieved from LinkedIn
            "auth_method": "linkedin",
            "subscription_status": "free",
            "message_count": 0
        }
        
        return user_data
    
    except Exception as e:
        st.error(f"Error processing LinkedIn callback: {str(e)}")
        return None

def verify_tech_background(profile_data, position_data):
    """
    Verify if the user has a tech background based on LinkedIn data
    This is a simplified implementation - in a real app, you'd use more sophisticated verification
    """
    # For demo purposes, we'll assume all users are tech professionals
    # In a real app, you'd check job titles, skills, etc.
    return True
