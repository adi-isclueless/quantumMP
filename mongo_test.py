import streamlit as st
from pymongo import MongoClient
from bson import ObjectId


def main():
    """Simple smoke test for MongoDB connectivity via st.secrets['uri']."""
    mongo_uri = st.secrets["uri"]
    client = MongoClient(mongo_uri)
    db = client.get_database("quantum_test")
    collection = db.get_collection("connectivity_checks")

    doc = {
        "_id": ObjectId(),
        "message": "MongoDB connection successful!",
        "source": "mongo_test.py",
    }
    collection.insert_one(doc)
    count = collection.count_documents({})

    st.write("Inserted document:", doc)
    st.write("Total documents in connectivity_checks:", count)


if __name__ == "__main__":
    main()

