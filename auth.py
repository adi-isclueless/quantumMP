"""
Authentication module for Quantum Virtual Labs
Handles user login, logout, and session management
"""

import streamlit as st
import hashlib
import json
import os
from pathlib import Path

# Simple file-based user storage (in production, use a database)
USERS_FILE = "users.json"

def init_users_file():
    """Initialize users file if it doesn't exist"""
    if not os.path.exists(USERS_FILE):
        # Default admin user (password: admin123)
        default_users = {
            "admin": {
                "password": hash_password("admin123"),
                "name": "Admin User",
                "email": "admin@vesit.ac.in"
            }
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed

def register_user(username: str, password: str, name: str, email: str = "") -> bool:
    """Register a new user"""
    init_users_file()
    
    # Load existing users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = {}
    
    # Check if user already exists
    if username in users:
        return False
    
    # Add new user
    users[username] = {
        "password": hash_password(password),
        "name": name,
        "email": email
    }
    
    # Save users
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    return True

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user"""
    init_users_file()
    
    if not os.path.exists(USERS_FILE):
        return False
    
    # Load users
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    # Check if user exists and password matches
    if username in users:
        return verify_password(password, users[username]["password"])
    
    return False

def get_user_info(username: str) -> dict:
    """Get user information"""
    init_users_file()
    
    if not os.path.exists(USERS_FILE):
        return None
    
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username in users:
        user_info = users[username].copy()
        user_info.pop("password", None)  # Don't return password
        return user_info
    
    return None

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
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                user_info = get_user_info(username)
                st.session_state.user_name = user_info.get("name", username)
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
    st.session_state.user_name = None
    st.rerun()

def require_auth():
    """Decorator to require authentication"""
    init_session_state()
    if not st.session_state.authenticated:
        login_page()
        st.stop()

