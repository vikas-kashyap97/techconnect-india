#!/bin/bash

# Creating the README.md file in one go
cat > README.md << 'EOF'
# TechConnect India App

This is a web application for TechConnect India, a platform exclusively for IT professionals to sign up, log in, and complete their profiles. The app uses **Streamlit** for frontend development, **Clerk** for authentication, and various backend processes for user management and profile completion.

## Features

- **Sign Up / Login**: Users can sign up and log in using Clerk authentication.
- **Profile Completion**: Users are required to complete their profiles by providing tech background information and verifying their tech skills.
- **Tech Background Verification**: Users can either upload a resume or manually input their tech skills to verify their background.
- **User Management**: The app creates a new user record in the database after profile completion.

## Prerequisites

Before running the app, ensure you have the following installed:

- Python 3.x
- Streamlit (`pip install streamlit`)
- Clerk API Key (sign up on [Clerk](https://clerk.dev/) for authentication)
- Optional: PDF parser for resume verification (if you want to implement resume parsing logic).

## Setup Instructions

```bash
# Clone the repository
git clone https://github.com/vikas-kashyap97/techconnect-india.git
cd techconnect-india

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up Clerk API key
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your-clerk-publishable-key"
# On Windows, use:
# set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-clerk-publishable-key

# Run the app
streamlit run app.py

# Access the app in your browser
# http://localhost:8501
