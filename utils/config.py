import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Clerk authentication configuration
CLERK_API_KEY = os.getenv("CLERK_API_KEY")
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API")

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# ChromaDB configuration
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# Application configuration
MAX_FREE_MESSAGES = 50
SUBSCRIPTION_PLANS = {
    "monthly": {
        "name": "Monthly",
        "price": 299,
        "duration_days": 30
    },
    "half_yearly": {
        "name": "6 Months",
        "price": 1599,
        "duration_days": 180
    },
    "yearly": {
        "name": "Yearly",
        "price": 2999,
        "duration_days": 365
    }
}
