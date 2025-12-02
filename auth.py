"""
Authentication module for Quantum Playground
Handles user login, logout, and OTP-based email verification
"""

import streamlit as st
import bcrypt
import smtplib
import re
import random
import string
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from db import get_database
from progress_store import load_user_progress_into_session


def _users_collection():
    db = get_database()
    db.users.create_index("username", unique=True)
    
    # Drop the old sparse email index if it exists, then create new one
    try:
        db.users.drop_index("email_1")
    except Exception:
        pass  # Index doesn't exist, that's fine
    
    db.users.create_index("email", unique=True)
    return db.users


def _otp_collection():
    """Get OTP collection for temporary OTP storage"""
    db = get_database()
    # Create TTL index to automatically delete expired OTPs after 10 minutes
    db.otp_tokens.create_index("created_at", expireAfterSeconds=600)
    return db.otp_tokens


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def generate_otp(length: int = 6) -> str:
    """Generate a random 6-digit OTP."""
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email: str, otp: str, username: str = None) -> bool:
    """
    Send OTP via email using SMTP.
    
    Requires Streamlit secrets:
    - server: SMTP server (e.g., smtp.gmail.com)
    - port: SMTP port (e.g., 587)
    - email: Sender email
    - password: SMTP password (Gmail App Password)
    
    Returns: True if email sent successfully, False otherwise
    """
    try:
        # Try to get SMTP credentials from Streamlit secrets
        smtp_server = st.secrets.get("server")
        smtp_port = int(st.secrets.get("port", 587))
        smtp_email = st.secrets.get("email")
        smtp_password = st.secrets.get("password")
        
        if not smtp_email or not smtp_password:
            st.warning("Email service not configured. Please set SMTP credentials in secrets.toml")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = email
        msg['Subject'] = 'Your Quantum Playground OTP Code'
        
        # Email body with OTP
        body = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; background-color: #f5f5f5; padding: 20px;">
                <div style="background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto;">
                    <h2 style="color: #1a237e; text-align: center; margin-bottom: 20px;">Quantum Playground</h2>
                    
                    <p style="color: #333; font-size: 16px;">
                        Hello{f' <strong>{username}</strong>' if username else ''},
                    </p>
                    
                    <p style="color: #666; font-size: 14px;">
                        Your one-time password (OTP) for secure authentication is:
                    </p>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; text-align: center; margin: 25px 0;">
                        <p style="font-size: 12px; color: #fff; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 2px;">Your OTP Code</p>
                        <p style="font-size: 48px; color: #fff; font-weight: bold; margin: 0; letter-spacing: 8px;">{otp}</p>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; text-align: center;">
                        <strong>Valid for 10 minutes only</strong>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 12px;">
                        <strong>Security Note:</strong> Never share this code with anyone. Quantum Playground support will never ask for your OTP.
                    </p>
                    
                    <p style="color: #999; font-size: 12px;">
                        If you didn't request this code, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
        
        return True
        
    except KeyError as e:
        st.error(f"Missing SMTP configuration: {e}")
        return False
    except Exception as e:
        st.error(f"Error sending OTP email: {str(e)}")
        return False


def create_otp_record(email: str) -> str:
    """Create and store an OTP record in MongoDB with rate limiting"""
    otp_collection = _otp_collection()
    
    # Check for recent OTP requests (rate limiting - 60 seconds cooldown)
    recent_otp = otp_collection.find_one({
        "email": email,
        "created_at": {"$gte": datetime.utcnow() - timedelta(seconds=60)}
    })
    
    if recent_otp:
        # Calculate remaining cooldown time
        elapsed = (datetime.utcnow() - recent_otp["created_at"]).total_seconds()
        remaining = 60 - int(elapsed)
        raise ValueError(f"Please wait {remaining} seconds before requesting another OTP")
    
    otp = generate_otp()
    
    # Delete any existing OTP for this email
    otp_collection.delete_many({"email": email})
    
    otp_collection.insert_one({
        "email": email,
        "otp": otp,
        "created_at": datetime.utcnow(),
        "verified": False
    })
    
    return otp


def verify_otp(email: str, provided_otp: str) -> bool:
    """Verify the provided OTP against stored OTP"""
    otp_collection = _otp_collection()
    record = otp_collection.find_one({"email": email})
    
    if not record:
        return False
    
    # Check if OTP matches
    if record.get("otp") == provided_otp:
        # Mark as verified
        otp_collection.update_one(
            {"_id": record["_id"]},
            {"$set": {"verified": True}}
        )
        return True
    
    return False


def clear_otp(email: str):
    """Clear OTP records for an email"""
    otp_collection = _otp_collection()
    otp_collection.delete_many({"email": email})


def register_user(username: str, password: str, name: str, email: str) -> bool:
    """Register a new user in MongoDB. Email is required."""
    users = _users_collection()
    
    # Validate inputs
    if not username or not password or not name or not email:
        return False
    
    if not is_valid_email(email):
        return False
    
    if users.find_one({"username": username}):
        return False
    
    if users.find_one({"email": email}):
        return False

    users.insert_one(
        {
            "username": username,
            "password": hash_password(password),
            "name": name,
            "email": email,
            "email_verified": False,
            "created_at": datetime.utcnow(),
        }
    )
    
    return True


def authenticate_user(username_or_email: str, password: str):
    """Authenticate a user using username or email and password."""
    users = _users_collection()
    
    # Try to find user by username or email
    user = None
    if is_valid_email(username_or_email):
        # If it's an email format, search by email
        user = users.find_one({"email": username_or_email})
    else:
        # Otherwise search by username
        user = users.find_one({"username": username_or_email})
    
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def get_user_info(username: str) -> dict:
    """Get user information without password."""
    user = _users_collection().find_one({"username": username}, {"password": 0})
    return user


def update_user_name(user_id, new_name: str) -> bool:
    """Update user's full name"""
    from bson.objectid import ObjectId
    users = _users_collection()
    
    if not new_name or len(new_name.strip()) == 0:
        return False
    
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"name": new_name.strip()}}
    )
    return result.modified_count > 0


def update_username(user_id, new_username: str) -> tuple[bool, str]:
    """Update user's username. Returns (success, error_message)"""
    from bson.objectid import ObjectId
    users = _users_collection()
    
    if not new_username or len(new_username.strip()) < 3:
        return False, "Username must be at least 3 characters long"
    
    # Check if username already exists
    existing = users.find_one({"username": new_username.strip()})
    if existing and str(existing["_id"]) != user_id:
        return False, "Username already taken"
    
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"username": new_username.strip()}}
    )
    return (result.modified_count > 0, "")


def update_email(user_id, new_email: str) -> tuple[bool, str]:
    """Update user's email (requires OTP verification). Returns (success, error_message)"""
    from bson.objectid import ObjectId
    users = _users_collection()
    
    if not is_valid_email(new_email):
        return False, "Invalid email format"
    
    # Check if email already exists
    existing = users.find_one({"email": new_email})
    if existing and str(existing["_id"]) != user_id:
        return False, "Email already in use"
    
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"email": new_email, "email_verified": True}}
    )
    return (result.modified_count > 0, "")


def update_password(user_id, old_password: str, new_password: str) -> tuple[bool, str]:
    """Update user's password. Returns (success, error_message)"""
    from bson.objectid import ObjectId
    users = _users_collection()
    
    # Verify old password
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return False, "User not found"
    
    if not verify_password(old_password, user["password"]):
        return False, "Current password is incorrect"
    
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters long"
    
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hash_password(new_password)}}
    )
    return (result.modified_count > 0, "")


def init_session_state():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'lab_progress' not in st.session_state:
        st.session_state.lab_progress = {}
    if 'quiz_scores' not in st.session_state:
        st.session_state.quiz_scores = {}
    if 'otp_step' not in st.session_state:
        st.session_state.otp_step = None  # 'registration', or None


def login_page():
    """Display login and registration page with OTP verification for registration only"""
    st.title("Quantum Playground")
    st.markdown("---")
    
    init_session_state()
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    # ============ TAB 1: LOGIN ============
    with tab1:
        st.markdown("### Login to Your Account")
        
        # Standard login form with username/email and password
        login_identifier = st.text_input(
            "Username or Email", 
            key="login_identifier_input", 
            placeholder="Enter your username or email"
        )
        login_password = st.text_input(
            "Password", 
            type="password", 
            key="login_password_input",
            placeholder="Enter your password"
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                if not login_identifier or not login_password:
                    st.error("Please enter both username/email and password")
                else:
                    with st.spinner("Authenticating..."):
                        user_doc = authenticate_user(login_identifier, login_password)
                        if user_doc:
                            st.session_state.authenticated = True
                            st.session_state.username = user_doc['username']
                            st.session_state.user_id = str(user_doc["_id"])
                            st.session_state.user_name = user_doc.get("name", user_doc['username'])
                            st.session_state.email = user_doc.get('email', '')
                            st.session_state.view_mode = "welcome"  # Send to welcome page
                            load_user_progress_into_session(user_doc["_id"])
                            
                            st.success(f"Welcome back, {user_doc.get('name', '')}!")
                            st.balloons()
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid username/email or password")
        with col2:
            if st.button("Forgot Password?", use_container_width=True):
                st.session_state.otp_step = 'forgot_password'
                st.rerun()
        
        # Forgot Password Flow
        if st.session_state.otp_step == 'forgot_password':
            st.markdown("---")
            st.markdown("### 🔐 Reset Your Password")
            st.info("Enter your email address to receive a password reset OTP")
            
            reset_email = st.text_input("Email Address", key="reset_email_input", placeholder="your@email.com")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Send Reset OTP", type="primary", use_container_width=True):
                    if not reset_email or not is_valid_email(reset_email):
                        st.error("Please enter a valid email address")
                    else:
                        # Check if email exists
                        users = _users_collection()
                        user = users.find_one({"email": reset_email})
                        if user:
                            with st.spinner("Sending OTP..."):
                                try:
                                    otp = create_otp_record(reset_email)
                                    if send_otp_email(reset_email, otp, user.get('name', 'User')):
                                        st.session_state.otp_step = 'reset_verify_otp'
                                        st.session_state.reset_email = reset_email
                                        st.success("OTP sent to your email!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to send OTP. Please try again.")
                                except ValueError as e:
                                    st.warning(f"⏱️ {str(e)}")
                        else:
                            # Don't reveal if email exists or not for security
                            st.info("If this email is registered, you will receive an OTP shortly.")
            with col2:
                if st.button("Back to Login", use_container_width=True):
                    st.session_state.otp_step = None
                    st.rerun()
        
        elif st.session_state.otp_step == 'reset_verify_otp':
            st.markdown("---")
            st.markdown("### ✅ Verify OTP")
            st.text(f"Email: {st.session_state.reset_email}")
            
            reset_otp = st.text_input("Enter OTP (6 digits)", max_chars=6, key="reset_otp_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify OTP", type="primary", use_container_width=True):
                    if verify_otp(st.session_state.reset_email, reset_otp):
                        st.session_state.otp_step = 'reset_new_password'
                        st.rerun()
                    else:
                        st.error("Invalid OTP. Please try again.")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.otp_step = None
                    st.session_state.reset_email = None
                    st.rerun()
        
        elif st.session_state.otp_step == 'reset_new_password':
            st.markdown("---")
            st.markdown("### 🔑 Set New Password")
            
            new_pass = st.text_input("New Password", type="password", key="reset_new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reset_confirm_pass")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Reset Password", type="primary", use_container_width=True):
                    if not new_pass or len(new_pass) < 8:
                        st.error("Password must be at least 8 characters long")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match")
                    else:
                        # Update password
                        users = _users_collection()
                        result = users.update_one(
                            {"email": st.session_state.reset_email},
                            {"$set": {"password": hash_password(new_pass)}}
                        )
                        if result.modified_count > 0:
                            clear_otp(st.session_state.reset_email)
                            st.success("✅ Password reset successful! You can now login with your new password.")
                            st.session_state.otp_step = None
                            st.session_state.reset_email = None
                            import time
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Failed to reset password. Please try again.")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.otp_step = None
                    st.session_state.reset_email = None
                    st.rerun()
    
    # ============ TAB 2: REGISTER ============
    with tab2:
        st.markdown("### Create New Account")
        
        if st.session_state.otp_step == 'registration':
            # OTP verification screen for registration
            st.info("An OTP has been sent to your email. Please enter it to complete registration.")
            reg_email = st.session_state.get('pending_reg_email', '')
            st.text(f"Verifying: {reg_email}")
            
            otp_input = st.text_input("Enter OTP (6 digits)", max_chars=6, key="reg_otp_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Verify OTP", type="primary", use_container_width=True):
                    if not otp_input or len(otp_input) != 6:
                        st.error("Please enter a valid 6-digit OTP")
                    else:
                        with st.spinner("Verifying OTP and completing registration..."):
                            if verify_otp(reg_email, otp_input):
                                # Create account and auto-login
                                user_doc = _users_collection().find_one({"email": reg_email})
                                if user_doc:
                                    st.session_state.authenticated = True
                                    st.session_state.username = user_doc['username']
                                    st.session_state.user_id = str(user_doc["_id"])
                                    st.session_state.user_name = user_doc.get("name", user_doc['username'])
                                    st.session_state.email = user_doc.get('email', '')
                                    st.session_state.otp_step = None
                                    st.session_state.view_mode = "welcome"  # Send to welcome page
                                    load_user_progress_into_session(user_doc["_id"])
                                    
                                    # Update email_verified flag
                                    _users_collection().update_one(
                                        {"_id": user_doc["_id"]},
                                        {"$set": {"email_verified": True}}
                                    )
                                    
                                    st.success(f"Registration Complete! Welcome, {user_doc.get('name', '')}!")
                                    st.balloons()
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                            else:
                                st.error("Invalid OTP. Please try again.")
            
            with col2:
                if st.button("Back", use_container_width=True):
                    st.session_state.otp_step = None
                    st.rerun()
        
        else:
            # Registration form
            reg_username = st.text_input("Username", key="reg_username", help="Choose a unique username (3-20 characters)")
            reg_name = st.text_input("Full Name", key="reg_name", help="Your full name")
            reg_email = st.text_input("Email", key="reg_email", help="Required for OTP verification", placeholder="your@email.com")
            reg_password = st.text_input("Password", type="password", key="reg_password", help="Minimum 8 characters recommended")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Create Account & Send OTP", type="primary", use_container_width=True):
                # Validation
                if not reg_username or not reg_name or not reg_password or not reg_email:
                    st.error("Please fill in all required fields")
                elif len(reg_username) < 3:
                    st.error("Username must be at least 3 characters long")
                elif len(reg_password) < 8:
                    st.error("Password must be at least 8 characters long")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match")
                elif not is_valid_email(reg_email):
                    st.error("Please enter a valid email address")
                else:
                # Attempt registration
                    with st.spinner("Creating account..."):
                        if register_user(reg_username, reg_password, reg_name, reg_email):
                            # Account created, now send OTP
                            with st.spinner("Sending OTP to your email..."):
                                try:
                                    otp = create_otp_record(reg_email)
                                    if send_otp_email(reg_email, otp, reg_name):
                                        st.session_state.otp_step = 'registration'
                                        st.session_state.pending_reg_email = reg_email
                                        st.success("Account created! OTP sent to your email.")
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to send OTP. Please try again or contact support.")
                                except ValueError as e:
                                    st.warning(f"⏱️ {str(e)}")
                                    st.rerun()
                                else:
                                    st.error("Failed to send OTP. Account created but please try logging in later.")
                        else:
                            st.error("Registration failed. Username or email may already exist.")


def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.otp_step = None
    st.rerun()


def require_auth():
    """Decorator to require authentication"""
    init_session_state()
    if not st.session_state.authenticated:
        login_page()
        st.stop()