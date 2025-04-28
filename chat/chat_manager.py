from database.chat_operations import send_message as db_send_message
from database.chat_operations import get_chat_history as db_get_chat_history
from database.user_operations import update_user
import streamlit as st

def initialize_chat(user_email, match_email):
    """
    Initialize a chat session between two users
    """
    # Get chat history
    chat_history = db_get_chat_history(user_email, match_email)
    
    # Store in session state
    st.session_state.chat_messages = chat_history
    
    return chat_history

def send_message(sender_email, receiver_email, message):
    """
    Send a message and update the chat history
    """
    # Store the message in the database
    message_id = db_send_message(sender_email, receiver_email, message)
    
    # Update the chat history in session state
    chat_history = db_get_chat_history(sender_email, receiver_email)
    st.session_state.chat_messages = chat_history
    
    return message_id

def get_chat_history(user_email, match_email):
    """
    Get the chat history between two users
    """
    return db_get_chat_history(user_email, match_email)
