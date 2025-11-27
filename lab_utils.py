import streamlit as st

# Small helper to render multiple LaTeX formulas with optional captions
def display_formulas(title=None, formulas=None):
    if not formulas:
        return
    if title:
        st.markdown(f"**{title}**")
    for f in formulas:
        try:
            st.latex(f)
        except Exception:
            # fallback to code block if latex fails
            st.code(f)
