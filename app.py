import streamlit as st
import os
from dotenv import load_dotenv
from auth.clerk_auth import get_user_token, get_user_data, verify_session
from auth.resume_parser import parse_resume
from database.chroma_connection import get_chroma_client
from database.user_operations import create_user, get_user_by_email, update_user
from chat.chat_manager import initialize_chat, send_message, get_chat_history
from utils.matching import find_random_match, find_city_match
from moderation.language_filter import check_message_toxicity
from payments.payment_gateway import create_subscription, verify_payment, get_subscription_plans

# Load environment variables
load_dotenv()

# Initialize ChromaDB
chroma_client = get_chroma_client()

# Page configuration
st.set_page_config(
    page_title="TechConnect India",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin-bottom: 1rem;
    }
    .chat-message-user {
        background-color: #E9F7EF;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        text-align: right;
    }
    .chat-message-other {
        background-color: #EBF5FB;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .message-count {
        font-size: 0.8rem;
        color: #777;
        text-align: center;
    }
    .payment-section {
        background-color: #F8F9F9;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
    }
    .clerk-auth-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 20px 0;
    }
    .clerk-button {
        background-color: #4ECDC4;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-decoration: none;
        margin: 10px 0;
        cursor: pointer;
        border: none;
    }
    .profile-completion {
        background-color: #F8F9F9;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    iframe {
        width: 100%;
        height: 500px;
        border: none;
    }
    .subscription-plan {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .subscription-plan:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .subscription-plan.selected {
        border: 2px solid #4ECDC4;
        background-color: rgba(78, 205, 196, 0.1);
    }
    .plan-price {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FF6B6B;
    }
    .plan-duration {
        font-size: 0.9rem;
        color: #777;
    }
    .plan-features {
        margin: 10px 0;
        padding-left: 20px;
    }
    .plan-features li {
        margin: 5px 0;
    }
    .payment-button {
        background-color: #FF6B6B;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .payment-button:hover {
        background-color: #ff5252;
        transform: translateY(-2px);
    }
    .auth-option {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .auth-option:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .auth-option h3 {
        color: #4ECDC4;
    }
    .auth-option p {
        color: #666;
    }
    .nav-button {
        width: 100%;
        text-align: left;
        margin: 5px 0;
        padding: 10px;
        border-radius: 5px;
        background-color: transparent;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .nav-button:hover {
        background-color: rgba(78, 205, 196, 0.1);
    }
    .nav-button.active {
        background-color: #4ECDC4;
        color: white;
    }
    .welcome-container {
        text-align: center;
        padding: 40px 20px;
    }
    .welcome-container h1 {
        font-size: 3rem;
        color: #FF6B6B;
        margin-bottom: 20px;
    }
    .welcome-container p {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 30px;
    }
    .welcome-buttons {
        display: flex;
        justify-content: center;
        gap: 20px;
    }
    .welcome-button {
        background-color: #4ECDC4;
        color: white;
        padding: 12px 30px;
        border-radius: 5px;
        border: none;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .welcome-button:hover {
        background-color: #3dbdb3;
        transform: translateY(-2px);
    }
    .welcome-button.secondary {
        background-color: #FF6B6B;
    }
    .welcome-button.secondary:hover {
        background-color: #ff5252;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_match' not in st.session_state:
    st.session_state.current_match = None
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'message_count' not in st.session_state:
    st.session_state.message_count = 0
if 'payment_link' not in st.session_state:
    st.session_state.payment_link = None
if 'clerk_token' not in st.session_state:
    st.session_state.clerk_token = None
if 'profile_completed' not in st.session_state:
    st.session_state.profile_completed = False
if 'selected_plan' not in st.session_state:
    st.session_state.selected_plan = None
if 'page' not in st.session_state:
    st.session_state.page = "Welcome"  # default page

# Main app header
st.markdown("<h1 class='main-header'>TechConnect India 🇮🇳</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Connect with IT professionals across India</p>", unsafe_allow_html=True)

# Check if user is authenticated with Clerk
clerk_token = get_user_token()
if clerk_token and clerk_token != st.session_state.clerk_token:
    st.session_state.clerk_token = clerk_token
    # Get user data from Clerk
    clerk_user_data = get_user_data(clerk_token)
    if clerk_user_data:
        # Check if user exists in our database
        existing_user = get_user_by_email(clerk_user_data['email'])
        if existing_user:
            st.session_state.user = existing_user
            st.session_state.message_count = existing_user.get('message_count', 0)
            st.session_state.profile_completed = True
            if st.session_state.page == "Welcome" or st.session_state.page == "Login" or st.session_state.page == "SignUp":
                st.session_state.page = "Profile"
        else:
            # New user, need to complete profile
            st.session_state.user = {
                "name": clerk_user_data.get('name', ''),
                "email": clerk_user_data.get('email', ''),
                "profile_image": clerk_user_data.get('profile_image', ''),
                "auth_method": "clerk"
            }
            st.session_state.profile_completed = False
            st.session_state.page = "Complete Profile"

# Function to change page
def change_page(page_name):
    st.session_state.page = page_name
    st.rerun()


# Sidebar for navigation
with st.sidebar:
    if st.session_state.user:
        # User is logged in
        st.image("assets/placeholder.png", width=150)
        st.markdown(r"Navigation")
        st.write(f"Welcome, {st.session_state.user['name']}!")
        
        if st.session_state.profile_completed:
            st.write(f"Messages sent: {st.session_state.message_count}/50")
            
            # Display subscription status
            if st.session_state.user.get('subscription_status') == 'paid':
                st.success("Premium Member")
            else:
                st.info("Free Account")
            
            # Navigation buttons
            nav_buttons = {
                "Profile": "Profile",
                "Find Connections": "Find Connections",
                "Chat": "Chat"
            }
            
            for button_text, page_name in nav_buttons.items():
                button_class = "nav-button active" if st.session_state.page == page_name else "nav-button"
                if st.button(button_text, key=f"nav_{page_name}", help=f"Go to {page_name}", use_container_width=True):
                    change_page(page_name)
        
        if st.button("Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            
            # Initialize default values
            st.session_state.page = "Welcome"
            st.session_state.user = None
            
            # Add JavaScript to clear Clerk session
            st.markdown("""
            <script>
                if (window.Clerk) {
                    window.Clerk.signOut().then(() => {
                        window.location.reload();
                    });
                }
            </script>
            """, unsafe_allow_html=True)
            
            st.rerun()

    else:
        # User is not logged in
        st.image("assets/placeholder.png", width=150)
        st.markdown("## Welcome")
        st.info(r"Please login or sign up to continue")
        
        # Navigation buttons for non-logged in users
        if st.button("Home", key="nav_welcome", use_container_width=True):
            change_page("Welcome")
        
        if st.button("Login", key="nav_login", use_container_width=True):
            change_page("Login")
        
        if st.button("Sign Up", key="nav_signup", use_container_width=True):
            change_page("SignUp")

# Main content area based on current page
if st.session_state.page == "Welcome":
    # Welcome page
    st.markdown("""
    <div class="welcome-container">
        <h1>Welcome to TechConnect India</h1>
        <p>Connect with IT professionals across India, find mentors, collaborators, or just make new friends in the tech industry.</p>
        <div class="welcome-buttons">
            <button onclick="changePage('Login')" class="welcome-button">Login</button>
            <button onclick="changePage('SignUp')" class="welcome-button secondary">Sign Up</button>
        </div>
    </div>
    
    <script>
    function changePage(page) {
        // Use Streamlit's session state to change the page
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: page
        }, "*");
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Handle button clicks from JavaScript
    query_params = st.query_params
    if "page" in query_params:
        change_page(query_params["page"][0])

elif st.session_state.page == "Login":
    # Login page
    st.markdown("<h2 class='sub-header'>Login to Your Account</h2>", unsafe_allow_html=True)
    
    # Embed Clerk authentication component
    clerk_publishable_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    
    st.markdown(f"""
    <div class="clerk-auth-container">
        <div id="clerk-sign-in"></div>
        <p>Secure authentication powered by Clerk.com</p>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"></script>
    <script>
        // Initialize Clerk
        const clerkPublishableKey = '{clerk_publishable_key}';
        
        if (!window.clerkLoaded) {{
            window.clerkLoaded = true;
            try {{
                const clerk = window.Clerk = Clerk.load(clerkPublishableKey);
                
                clerk.load()
                    .then(function() {{
                        const signInDiv = document.getElementById('clerk-sign-in');
                        if (signInDiv) {{
                            clerk.mountSignIn(signInDiv);
                        }}
                        
                        // Listen for authentication events
                        clerk.addListener(function(event) {{
                            if (event.user) {{
                                // User is signed in, reload the page to update session
                                window.location.reload();
                            }}
                        }});
                    }})
                    .catch(function(error) {{
                        console.error('Error loading Clerk:', error);
                    }});
            }} catch (error) {{
                console.error('Error initializing Clerk:', error);
            }}
        }}
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p>Don't have an account? <a href="#" onclick="changePage('SignUp')">Sign Up</a></p>
    </div>
    
    <script>
    function changePage(page) {
        // Use Streamlit's session state to change the page
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: page
        }, "*");
    }
    </script>
    """, unsafe_allow_html=True)

elif st.session_state.page == "SignUp":
    # Sign Up page
    st.markdown("<h2 class='sub-header'>Create a New Account</h2>", unsafe_allow_html=True)
    
    # Embed Clerk authentication component
    clerk_publishable_key = os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")
    
    st.markdown(f"""
    <div class="clerk-auth-container">
        <div id="clerk-sign-up"></div>
        <p>Secure authentication powered by Clerk.com</p>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"></script>
    <script>
        // Initialize Clerk
        const clerkPublishableKey = '{clerk_publishable_key}';
        
        if (!window.clerkLoaded) {{
            window.clerkLoaded = true;
            try {{
                const clerk = window.Clerk = Clerk.load(clerkPublishableKey);
                
                clerk.load()
                    .then(function() {{
                        const signUpDiv = document.getElementById('clerk-sign-up');
                        if (signUpDiv) {{
                            clerk.mountSignUp(signUpDiv);
                        }}
                        
                        // Listen for authentication events
                        clerk.addListener(function(event) {{
                            if (event.user) {{
                                // User is signed in, reload the page to update session
                                window.location.reload();
                            }}
                        }});
                    }})
                    .catch(function(error) {{
                        console.error('Error loading Clerk:', error);
                    }});
            }} catch (error) {{
                console.error('Error initializing Clerk:', error);
            }}
        }}
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <p>Already have an account? <a href="#" onclick="changePage('Login')">Login</a></p>
    </div>
    
    <script>
    function changePage(page) {
        // Use Streamlit's session state to change the page
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: page
        }, "*");
    }
    </script>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Complete Profile":
    # Profile completion page for new users
    st.markdown("<h2 class='sub-header'>Complete Your Profile</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="profile-completion">
        <p>To ensure TechConnect India remains a platform exclusively for IT professionals, 
        please complete your profile with your tech background information.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Form for profile completion
    with st.form("profile_completion_form"):
        city = st.text_input("City")
        
        # Tech background verification options
        verification_method = st.radio(
            "Verify your tech background",
            ["Upload Resume", "Enter Skills Manually"]
        )
        
        if verification_method == "Upload Resume":
            uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf")
            skills = []
        else:
            uploaded_file = None
            skills_input = st.text_input("Enter your tech skills (comma-separated)")
            skills = [skill.strip() for skill in skills_input.split(",")] if skills_input else []
        
        submit_button = st.form_submit_button("Complete Profile")
        
        if submit_button:
            is_tech_professional = False
            
            if verification_method == "Upload Resume" and uploaded_file:
                # Parse resume to verify tech background
                is_tech_professional, parsed_skills = parse_resume(uploaded_file)
                skills = parsed_skills
            elif verification_method == "Enter Skills Manually" and skills:
                # Simple verification based on number of skills
                is_tech_professional = len(skills) >= 3
            
            if is_tech_professional:
                # Update user data
                user_data = {
                    "name": st.session_state.user["name"],
                    "email": st.session_state.user["email"],
                    "city": city,
                    "skills": skills,
                    "auth_method": "clerk",
                    "subscription_status": "free",
                    "message_count": 0,
                    "profile_image": st.session_state.user.get("profile_image", "")
                }
                
                # Create user in database
                create_user(user_data)
                
                # Update session state
                st.session_state.user = user_data
                st.session_state.profile_completed = True
                st.session_state.page = "Profile"
                
                st.success("Profile completed successfully!")
                st.rerun()

            else:
                st.error("We couldn't verify your tech background. Please ensure you have relevant tech experience mentioned.")

elif st.session_state.page == "Profile":
    st.markdown("<h2 class='sub-header'>Your Profile</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Use profile image from Clerk if available, otherwise use placeholder
        profile_image = st.session_state.user.get('profile_image', "/placeholder.svg?height=200&width=200")
        st.image(profile_image, width=200)
    
    with col2:
        st.write(f"**Name:** {st.session_state.user['name']}")
        st.write(f"**Email:** {st.session_state.user['email']}")
        st.write(f"**City:** {st.session_state.user['city']}")
        st.write(f"**Skills:** {', '.join(st.session_state.user.get('skills', []))}")
        
        # Subscription status and upgrade option
        if st.session_state.user.get('subscription_status') != 'paid':
            st.markdown("<div class='payment-section'>", unsafe_allow_html=True)
            st.markdown("### Upgrade to Premium")
            st.write("Get city-based matching and unlimited messages!")
            
            # Get subscription plans
            subscription_plans = get_subscription_plans()
            
            # Display subscription plans
            cols = st.columns(len(subscription_plans))
            
            for i, (plan_id, plan) in enumerate(subscription_plans.items()):
                with cols[i]:
                    plan_class = "subscription-plan"
                    if st.session_state.selected_plan == plan_id:
                        plan_class += " selected"
                    
                    st.markdown(f"""
                    <div class="{plan_class}" id="plan-{plan_id}">
                        <h3>{plan['name']}</h3>
                        <div class="plan-price">₹{plan['price']}</div>
                        <div class="plan-duration">for {plan['duration']}</div>
                        <ul class="plan-features">
                            <li>City-based matching</li>
                            <li>Unlimited messages</li>
                            <li>Priority support</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select {plan['name']}", key=f"select_plan_{plan_id}"):
                        st.session_state.selected_plan = plan_id
                        st.rerun()

            
            if st.session_state.selected_plan:
                selected_plan = subscription_plans[st.session_state.selected_plan]
                st.markdown(f"**Selected Plan:** {selected_plan['name']} (₹{selected_plan['price']})")
                
                if st.button("Subscribe Now", key="subscribe_button"):
                    with st.spinner("Creating subscription..."):
                        subscription_id, payment_link = create_subscription(
                            st.session_state.user['email'],
                            st.session_state.selected_plan
                        )
                        
                        if payment_link:
                            st.session_state.payment_link = payment_link
                            st.markdown(f"<a href='{payment_link}' target='_blank' class='payment-button'>Complete Payment</a>", unsafe_allow_html=True)
                        else:
                            st.error("Failed to create subscription. Please try again.")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Payment verification
            if st.session_state.payment_link and st.button("I've completed payment"):
                with st.spinner("Verifying payment..."):
                    if verify_payment(st.session_state.user['email']):
                        st.session_state.user['subscription_status'] = 'paid'
                        update_user(st.session_state.user['email'], {'subscription_status': 'paid'})
                        st.success("Payment verified! You now have premium access.")
                        st.rerun()

                    else:
                        st.error("Payment verification failed. Please try again or contact support.")
        else:
            st.success("You have a premium subscription with unlimited messages and city-based matching!")

elif st.session_state.page == "Find Connections":
    st.markdown("<h2 class='sub-header'>Find Connections</h2>", unsafe_allow_html=True)
    
    if st.session_state.user.get('subscription_status') == 'paid':
        match_type = st.radio("Match type:", ["Random (All India)", "City-based"])
        
        if match_type == "Random (All India)":
            if st.button("Find Random Match"):
                with st.spinner("Finding a random match across India..."):
                    match = find_random_match(st.session_state.user['email'])
                    if match:
                        st.session_state.current_match = match
                        st.session_state.chat_messages = get_chat_history(
                            st.session_state.user['email'], 
                            match['email']
                        )
                        st.session_state.page = "Chat"
                        st.rerun()

                    else:
                        st.error("No matches available at the moment. Try again later.")
        else:
            if st.button("Find City Match"):
                with st.spinner(f"Finding a match in {st.session_state.user['city']}..."):
                    match = find_city_match(st.session_state.user['email'], st.session_state.user['city'])
                    if match:
                        st.session_state.current_match = match
                        st.session_state.chat_messages = get_chat_history(
                            st.session_state.user['email'], 
                            match['email']
                        )
                        st.session_state.page = "Chat"
                        st.rerun()

                    else:
                        st.error(f"No matches available in {st.session_state.user['city']} at the moment. Try again later.")
    else:
        if st.button("Find Random Match"):
            with st.spinner("Finding a random match across India..."):
                match = find_random_match(st.session_state.user['email'])
                if match:
                    st.session_state.current_match = match
                    st.session_state.chat_messages = get_chat_history(
                        st.session_state.user['email'], 
                        match['email']
                    )
                    st.session_state.page = "Chat"
                    st.rerun()

                else:
                    st.error("No matches available at the moment. Try again later.")
        
        st.info("Upgrade to premium for city-based matching!")
        
        # Get subscription plans
        subscription_plans = get_subscription_plans()
        
        # Display subscription plans
        cols = st.columns(len(subscription_plans))
        
        for i, (plan_id, plan) in enumerate(subscription_plans.items()):
            with cols[i]:
                plan_class = "subscription-plan"
                if st.session_state.selected_plan == plan_id:
                    plan_class += " selected"
                
                st.markdown(f"""
                <div class="{plan_class}" id="plan-{plan_id}">
                    <h3>{plan['name']}</h3>
                    <div class="plan-price">₹{plan['price']}</div>
                    <div class="plan-duration">for {plan['duration']}</div>
                    <ul class="plan-features">
                        <li>City-based matching</li>
                        <li>Unlimited messages</li>
                        <li>Priority support</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select {plan['name']}", key=f"select_plan_find_{plan_id}"):
                    st.session_state.selected_plan = plan_id
                    st.rerun()

        
        if st.session_state.selected_plan:
            selected_plan = subscription_plans[st.session_state.selected_plan]
            st.markdown(f"**Selected Plan:** {selected_plan['name']} (₹{selected_plan['price']})")
            
            if st.button("Subscribe Now", key="subscribe_button_find"):
                with st.spinner("Creating subscription..."):
                    subscription_id, payment_link = create_subscription(
                        st.session_state.user['email'],
                        st.session_state.selected_plan
                    )
                    
                    if payment_link:
                        st.session_state.payment_link = payment_link
                        st.markdown(f"<a href='{payment_link}' target='_blank' class='payment-button'>Complete Payment</a>", unsafe_allow_html=True)
                    else:
                        st.error("Failed to create subscription. Please try again.")

elif st.session_state.page == "Chat":
    st.markdown("<h2 class='sub-header'>Chat</h2>", unsafe_allow_html=True)
    
    if st.session_state.current_match:
        st.write(f"Chatting with: **{st.session_state.current_match['name']}** from {st.session_state.current_match['city']}")
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg['sender'] == st.session_state.user['email']:
                    st.markdown(f"<div class='chat-message-user'>{msg['message']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-message-other'>{msg['message']}</div>", unsafe_allow_html=True)
        
        # Message input
        if st.session_state.message_count >= 50 and st.session_state.user.get('subscription_status') != 'paid':
            st.warning("You've reached your free message limit. Upgrade to premium for unlimited messages!")
            
            # Get subscription plans
            subscription_plans = get_subscription_plans()
            
            # Display subscription plans
            cols = st.columns(len(subscription_plans))
            
            for i, (plan_id, plan) in enumerate(subscription_plans.items()):
                with cols[i]:
                    plan_class = "subscription-plan"
                    if st.session_state.selected_plan == plan_id:
                        plan_class += " selected"
                    
                    st.markdown(f"""
                    <div class="{plan_class}" id="plan-{plan_id}">
                        <h3>{plan['name']}</h3>
                        <div class="plan-price">₹{plan['price']}</div>
                        <div class="plan-duration">for {plan['duration']}</div>
                        <ul class="plan-features">
                            <li>City-based matching</li>
                            <li>Unlimited messages</li>
                            <li>Priority support</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Select {plan['name']}", key=f"select_plan_chat_{plan_id}"):
                        st.session_state.selected_plan = plan_id
                        st.rerun()

            
            if st.session_state.selected_plan:
                selected_plan = subscription_plans[st.session_state.selected_plan]
                st.markdown(f"**Selected Plan:** {selected_plan['name']} (₹{selected_plan['price']})")
                
                if st.button("Subscribe Now", key="subscribe_button_chat"):
                    with st.spinner("Creating subscription..."):
                        subscription_id, payment_link = create_subscription(
                            st.session_state.user['email'],
                            st.session_state.selected_plan
                        )
                        
                        if payment_link:
                            st.session_state.payment_link = payment_link
                            st.markdown(f"<a href='{payment_link}' target='_blank' class='payment-button'>Complete Payment</a>", unsafe_allow_html=True)
                        else:
                            st.error("Failed to create subscription. Please try again.")
        else:
            message = st.text_input("Type your message")
            
            if st.button("Send") and message:
                # Check for offensive content
                is_toxic = check_message_toxicity(message)
                
                if is_toxic:
                    st.error("Your message contains inappropriate content. Please revise and try again.")
                else:
                    # Send message
                    send_message(
                        st.session_state.user['email'],
                        st.session_state.current_match['email'],
                        message
                    )
                    
                    # Update message count for free users
                    if st.session_state.user.get('subscription_status') != 'paid':
                        st.session_state.message_count += 1
                        update_user(
                            st.session_state.user['email'], 
                            {'message_count': st.session_state.message_count}
                        )
                    
                    # Update chat history
                    st.session_state.chat_messages = get_chat_history(
                        st.session_state.user['email'],
                        st.session_state.current_match['email']
                    )
                    
                    st.rerun()

            
            if st.session_state.user.get('subscription_status') != 'paid':
                st.markdown(f"<div class='message-count'>Messages sent: {st.session_state.message_count}/50</div>", unsafe_allow_html=True)
    else:
        st.info("Find a connection first to start chatting!")
        if st.button("Go to Find Connections"):
            st.session_state.page = "Find Connections"
            st.rerun()


# Auto-refresh chat (simplified polling)
if st.session_state.page == "Chat" and st.session_state.current_match:
    st.empty()
    st.session_state.chat_messages = get_chat_history(
        st.session_state.user['email'],
        st.session_state.current_match['email']
    )

# Add Clerk script to every page
st.markdown(f"""
<script src="https://cdn.jsdelivr.net/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"></script>
<script>
    // Initialize Clerk
    const clerkPublishableKey = '{os.getenv("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY")}';
    
    if (!window.clerkInitialized) {{
        window.clerkInitialized = true;
        try {{
            const clerk = Clerk.load(clerkPublishableKey);
            
            // Set up event listener for page changes from JavaScript
            window.addEventListener('message', function(e) {{
                if (e.data.type === 'streamlit:setComponentValue') {{
                    // Change the page
                    const stateUpdateEvent = new CustomEvent('streamlit:componentStateChanged', {{
                        detail: {{
                            page: e.data.value
                        }}
                    }});
                    window.dispatchEvent(stateUpdateEvent);
                    
                    // Force a rerun
                    setTimeout(() => {{
                        window.location.reload();
                    }}, 100);
                }}
            }});
        }} catch (error) {{
            console.error('Error initializing Clerk:', error);
        }}
    }}
</script>
""", unsafe_allow_html=True)
