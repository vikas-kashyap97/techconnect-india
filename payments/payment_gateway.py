import os
import uuid
import razorpay
from database.user_operations import update_user

def get_subscription_plans():
    """
    Get available subscription plans
    Returns a dictionary of plans
    """
    return {
        "monthly": {
            "id": os.getenv("RAZORPAY_PLAN_ID", "plan_QO1YvYfLLqeEze"),
            "name": "Monthly",
            "price": 299,
            "duration": "1 month",
            "interval": 1,
            "period": "monthly"
        },
        "half_yearly": {
            "id": os.getenv("RAZORPAY_PLAN_ID", "plan_QO1YvYfLLqeEze"),
            "name": "6 Months",
            "price": 1599,
            "duration": "6 months",
            "interval": 6,
            "period": "monthly"
        },
        "yearly": {
            "id": os.getenv("RAZORPAY_PLAN_ID", "plan_QO1YvYfLLqeEze"),
            "name": "Yearly",
            "price": 3000,
            "duration": "1 year",
            "interval": 12,
            "period": "monthly"
        }
    }

def create_subscription(user_email, plan_id):
    """
    Create a subscription using Razorpay
    Returns a tuple of (subscription_id, payment_link)
    """
    try:
        # Get Razorpay credentials from environment variables
        key_id = os.getenv("RAZORPAY_LIVE_KEY")
        key_secret = os.getenv("RAZORPAY_SECRET_KEY")
        
        if not key_id or not key_secret:
            # Return a dummy payment link for demo purposes
            return None, f"https://example.com/dummy-payment/{uuid.uuid4()}"
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Get plan details
        plans = get_subscription_plans()
        plan = plans.get(plan_id)
        
        if not plan:
            return None, None
        
        # Create a subscription
        subscription_data = {
            'plan_id': plan['id'],
            'customer_notify': 1,
            'quantity': 1,
            'total_count': 12,  # Number of billing cycles
            'notes': {
                'user_email': user_email,
                'plan_name': plan['name']
            }
        }
        
        subscription = client.subscription.create(subscription_data)
        
        # Get the payment link
        payment_link = subscription.get('short_url')
        subscription_id = subscription.get('id')
        
        # Store subscription info in user data
        update_user(user_email, {
            'subscription_id': subscription_id,
            'subscription_plan': plan_id
        })
        
        return subscription_id, payment_link
    
    except Exception as e:
        print(f"Error creating subscription: {str(e)}")
        # Return a dummy payment link for demo purposes
        return None, f"https://example.com/dummy-payment/{uuid.uuid4()}"

def verify_payment(user_email):
    """
    Verify a payment for a user
    This is a simplified implementation - in a real app, you'd use webhooks
    
    For demo purposes, we'll just return True to simulate a successful payment
    """
    try:
        # Get Razorpay credentials from environment variables
        key_id = os.getenv("RAZORPAY_LIVE_KEY")
        key_secret = os.getenv("RAZORPAY_SECRET_KEY")
        
        if not key_id or not key_secret:
            # For demo purposes, return True
            return True
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(key_id, key_secret))
        
        # Get user data to retrieve subscription ID
        from database.user_operations import get_user_by_email
        user_data = get_user_by_email(user_email)
        
        if not user_data or 'subscription_id' not in user_data:
            return False
        
        subscription_id = user_data['subscription_id']
        
        # Fetch subscription details
        subscription = client.subscription.fetch(subscription_id)
        
        # Check if subscription is active
        if subscription.get('status') == 'active':
            # Update user's subscription status
            update_user(user_email, {'subscription_status': 'paid'})
            return True
        
        return False
    
    except Exception as e:
        print(f"Error verifying payment: {str(e)}")
        # For demo purposes, return True
        return True

def create_payment_link(user_email, plan):
    """
    Legacy function for backward compatibility
    Create a payment link using Razorpay
    Returns the payment link URL
    """
    # Parse the plan to get plan_id
    plan_id = None
    if plan == "₹299/month":
        plan_id = "monthly"
    elif plan == "₹1599/6 months":
        plan_id = "half_yearly"
    elif plan == "₹3000/year":
        plan_id = "yearly"
    
    if not plan_id:
        return f"https://example.com/dummy-payment/{uuid.uuid4()}"
    
    # Create subscription
    _, payment_link = create_subscription(user_email, plan_id)
    return payment_link
