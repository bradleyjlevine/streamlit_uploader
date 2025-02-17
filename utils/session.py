import streamlit as st
import time

SESSION_TIMEOUT = 4 * 60 * 60  # 4 hours in seconds

def get_session():
    """Ensure session state variables exist."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "cloud_id" not in st.session_state:
        st.session_state["cloud_id"] = None
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = None
    if "timestamp" not in st.session_state:
        st.session_state["timestamp"] = time.time()
    return st.session_state

def set_session(authenticated: bool, cloud_id: str, api_key: str):
    """Store authentication state and credentials securely."""
    st.session_state["authenticated"] = authenticated
    st.session_state["cloud_id"] = cloud_id
    st.session_state["api_key"] = api_key
    st.session_state["timestamp"] = time.time()

def is_session_expired():
    """Check if session has expired."""
    return (time.time() - st.session_state["timestamp"]) > SESSION_TIMEOUT

def logout():
    """Clear session state and log out user."""
    st.session_state["authenticated"] = False
    st.session_state["cloud_id"] = None
    st.session_state["api_key"] = None
    st.session_state["timestamp"] = 0
    st.rerun()
