import os

import streamlit as st
from pymongo import MongoClient


def _get_mongo_uri() -> str:
    """Retrieve Mongo connection string from Streamlit secrets or env."""
    if "uri" in st.secrets:
        return st.secrets["uri"]
    env_uri = os.environ.get("MONGO_URI")
    if not env_uri:
        raise RuntimeError("MongoDB URI not found in st.secrets['uri'] or env variable MONGO_URI")
    return env_uri


@st.cache_resource
def get_mongo_client() -> MongoClient:
    """Create a cached MongoDB client."""
    uri = _get_mongo_uri()
    return MongoClient(uri, serverSelectionTimeoutMS=5000)


def get_database():
    """Return the default application database."""
    client = get_mongo_client()
    db_name = st.secrets.get("mongo_db") or os.environ.get("MONGO_DB") or "quantum_virtual_lab"
    return client[db_name]

