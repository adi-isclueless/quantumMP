from datetime import datetime
from typing import Any, Dict

import streamlit as st
from bson import ObjectId

from db import get_database


def _ensure_session_progress():
    if "lab_progress" not in st.session_state:
        st.session_state.lab_progress = {}
    if "quiz_scores" not in st.session_state:
        st.session_state.quiz_scores = {}


def _current_user_object_id():
    user_id = st.session_state.get("user_id")
    if not user_id:
        return None
    if isinstance(user_id, ObjectId):
        return user_id
    try:
        return ObjectId(user_id)
    except Exception:
        return None


def load_user_progress_into_session(user_id):
    """Hydrate session state with persisted progress for this user."""
    _ensure_session_progress()
    db = get_database()
    user_oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)

    st.session_state.lab_progress = {}
    st.session_state.quiz_scores = {}

    cursor = db.lab_progress.find({"user_id": user_oid})
    for doc in cursor:
        lab_id = doc.get("lab_id")
        if not lab_id:
            continue
        if doc.get("progress_flags"):
            st.session_state.lab_progress[lab_id] = doc["progress_flags"]
        if doc.get("quiz_score"):
            st.session_state.quiz_scores[lab_id] = doc["quiz_score"]


def set_lab_progress_flag(lab_id: str, key: str, value: Any):
    """Update a progress flag both locally and in MongoDB."""
    _ensure_session_progress()
    st.session_state.lab_progress.setdefault(lab_id, {})[key] = value

    user_oid = _current_user_object_id()
    if not user_oid:
        return

    db = get_database()
    update = {
        "$set": {
            "progress_flags." + key: value,
            "lab_id": lab_id,
            "user_id": user_oid,
        },
        "$currentDate": {"updated_at": True},
        "$setOnInsert": {"created_at": datetime.utcnow()},
    }
    db.lab_progress.update_one({"user_id": user_oid, "lab_id": lab_id}, update, upsert=True)


def save_quiz_score(lab_id: str, score: Dict[str, Any]):
    """Persist quiz score and derived pass status."""
    _ensure_session_progress()
    st.session_state.quiz_scores[lab_id] = score
    passed = score.get("percentage", 0) >= 70
    if passed:
        st.session_state.lab_progress.setdefault(lab_id, {})["quiz_passed"] = True

    user_oid = _current_user_object_id()
    if not user_oid:
        return

    db = get_database()
    update = {
        "$set": {
            "quiz_score": score,
            "lab_id": lab_id,
            "user_id": user_oid,
        },
        "$currentDate": {"updated_at": True},
        "$setOnInsert": {"created_at": datetime.utcnow()},
    }
    if passed:
        update["$set"]["progress_flags.quiz_passed"] = True
    db.lab_progress.update_one({"user_id": user_oid, "lab_id": lab_id}, update, upsert=True)


def mark_certificate_generated(lab_id: str):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    set_lab_progress_flag(lab_id, "certificate_generated", True)
    set_lab_progress_flag(lab_id, "certificate_date", date_str)




