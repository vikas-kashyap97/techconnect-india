import random
from database.user_operations import get_all_users, get_users_by_city

def find_random_match(current_user_email):
    """
    Find a random match for the current user from all users
    Returns a user object or None if no match is found
    """
    # Get all users except the current user
    all_users = get_all_users(exclude_email=current_user_email)
    
    if not all_users:
        return None
    
    # Select a random user
    random_match = random.choice(all_users)
    
    return random_match

def find_city_match(current_user_email, city):
    """
    Find a random match for the current user from users in the same city
    Returns a user object or None if no match is found
    """
    # Get users from the same city except the current user
    city_users = get_users_by_city(city, exclude_email=current_user_email)
    
    if not city_users:
        return None
    
    # Select a random user
    random_match = random.choice(city_users)
    
    return random_match
