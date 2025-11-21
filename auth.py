"""
Authentication module for Quantum Virtual Labs
Handles user login, logout, and session management
"""

import streamlit as st
import bcrypt
from datetime import datetime

from db import get_database
from progress_store import load_user_progress_into_session


def _users_collection():
    db = get_database()
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True, sparse=True)
    return db.users


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(username: str, password: str, name: str, email: str = "") -> bool:
    """Register a new user in MongoDB."""
    users = _users_collection()
    if users.find_one({"username": username}):
        return False
    if email and users.find_one({"email": email}):
        return False

    users.insert_one(
        {
            "username": username,
            "password": hash_password(password),
            "name": name,
            "email": email,
            "created_at": datetime.utcnow(),
        }
    )
    return True


def authenticate_user(username: str, password: str):
    """Authenticate a user and return the document on success."""
    user = _users_collection().find_one({"username": username})
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return user


def get_user_info(username: str) -> dict:
    """Get user information without password."""
    user = _users_collection().find_one({"username": username}, {"password": 0})
    return user

def init_session_state():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'lab_progress' not in st.session_state:
        st.session_state.lab_progress = {}
    if 'quiz_scores' not in st.session_state:
        st.session_state.quiz_scores = {}

def login_page():
    """Display login page"""
    st.title("Quantum Virtual Labs - Login")
    st.markdown("---")
    
    init_session_state()
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            user_doc = authenticate_user(username, password)
            if user_doc:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_id = str(user_doc["_id"])
                st.session_state.user_name = user_doc.get("name", username)
                load_user_progress_into_session(user_doc["_id"])
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.markdown("### Create New Account")
        reg_username = st.text_input("Username", key="reg_username")
        reg_name = st.text_input("Full Name", key="reg_name")
        reg_email = st.text_input("Email (optional)", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", type="primary", use_container_width=True):
            if not reg_username or not reg_name or not reg_password:
                st.error("Please fill in all required fields")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match")
            elif register_user(reg_username, reg_password, reg_name, reg_email):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists")

def logout():
    """Logout the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.rerun()

def require_auth():
    """Decorator to require authentication"""
    init_session_state()
    if not st.session_state.authenticated:
        login_page()
        st.stop()

