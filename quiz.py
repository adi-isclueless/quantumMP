"""
Quiz module for testing knowledge after theory sections
"""

import streamlit as st
from translations import get_text
from lab_config import get_lab
from progress_store import save_quiz_score, set_lab_progress_flag

def render_quiz(lab_name: str):
    """Render quiz for a specific lab"""
    # Find lab config by name or ID
    from lab_config import LABS
    lab_config = None
    for name, config in LABS.items():
        if config["id"] == lab_name or name == lab_name or config.get("title") == lab_name:
            lab_config = config
            break
    
    if not lab_config or "quiz" not in lab_config:
        st.error(get_text("lab_not_found", st.session_state.get("language", "en")))
        return
    
    quiz = lab_config["quiz"]
    lang = st.session_state.get("language", "en")
    st.header(get_text("test_knowledge", lang))
    st.markdown(get_text("quiz_intro", lang))
    
    # Initialize session state for quiz
    quiz_key = f"quiz_{lab_config['id']}"
    if quiz_key not in st.session_state:
        st.session_state[quiz_key] = {
            "answers": [None] * len(quiz),
            "submitted": False,
            "score": 0
        }
    
    quiz_state = st.session_state[quiz_key]
    
    # Display questions
    for i, question_data in enumerate(quiz):
        st.markdown(f"### {get_text('question', lang)} {i+1}")
        st.markdown(question_data["question"])
        
        # Radio buttons for options
        answer = st.radio(
            get_text("select_answer", lang),
            question_data["options"],
            index=quiz_state["answers"][i] if quiz_state["answers"][i] is not None else None,
            key=f"q_{i}",
            disabled=quiz_state["submitted"]
        )
        
        # Store answer
        if answer:
            answer_index = question_data["options"].index(answer)
            quiz_state["answers"][i] = answer_index
        
        # Show result if submitted
        if quiz_state["submitted"]:
            correct_index = question_data["correct"]
            user_answer = quiz_state["answers"][i]
            
            if user_answer == correct_index:
                st.success(get_text("correct", lang))
            else:
                st.error(f"{get_text('incorrect', lang)} {get_text('correct_answer_is', lang)} {question_data['options'][correct_index]}")
            
            # Show explanation
            with st.expander(get_text("explanation", lang)):
                st.markdown(question_data["explanation"])
        
        st.divider()
    
    # Submit button
    col1, col2 = st.columns([1, 4])
    with col1:
        if not quiz_state["submitted"]:
            if st.button(get_text("submit_quiz", lang), type="primary", use_container_width=True):
                # Validate that all questions are answered
                unanswered = [i+1 for i, ans in enumerate(quiz_state["answers"]) if ans is None]
                if unanswered:
                    st.error(f"⚠️ Please answer all questions before submitting. Unanswered: {', '.join(map(str, unanswered))}")
                else:
                    # Calculate score
                    score = 0
                    for i, question_data in enumerate(quiz):
                        if quiz_state["answers"][i] == question_data["correct"]:
                            score += 1
                    
                    quiz_state["score"] = score
                    quiz_state["submitted"] = True
                    
                    # Store in session state
                    score_payload = {
                        "score": score,
                        "total": len(quiz),
                        "percentage": (score / len(quiz)) * 100
                    }
                    save_quiz_score(lab_config["id"], score_payload)
                    
                    st.rerun()
        else:
            # Show score
            score_percentage = (quiz_state["score"] / len(quiz)) * 100
            st.metric(get_text("your_score", lang), f"{quiz_state['score']}/{len(quiz)}", f"{score_percentage:.1f}%")
            
            if st.button(get_text("retake_quiz", lang), use_container_width=True):
                # Reset quiz
                st.session_state[quiz_key] = {
                    "answers": [None] * len(quiz),
                    "submitted": False,
                    "score": 0
                }
                st.rerun()
    
    # Show pass/fail message
    if quiz_state["submitted"]:
        score_percentage = (quiz_state["score"] / len(quiz)) * 100
        if score_percentage >= 70:
            st.success(f"{get_text('passed_with', lang)} {score_percentage:.1f}%")
            set_lab_progress_flag(lab_config["id"], "quiz_passed", True)
        else:
            st.warning(get_text("scored_review", lang).format(score=f"{score_percentage:.1f}%"))

def get_quiz_score(lab_id: str):
    """Get quiz score for a lab"""
    if "quiz_scores" not in st.session_state:
        return None
    return st.session_state.quiz_scores.get(lab_id)

def has_passed_quiz(lab_id: str):
    """Check if user has passed the quiz (>= 70%)"""
    score = get_quiz_score(lab_id)
    if score is None:
        return False
    return score["percentage"] >= 70

