import streamlit as st
from utils.auth import authenticate_elasticsearch
from utils.session import set_session, is_session_expired, logout

st.title("🔑 Login to Elasticsearch")

if is_session_expired():
    logout()

cloud_id = st.text_input("Cloud ID", type="password")
api_key = st.text_input("API Key", type="password")

if st.button("Login"):
    if authenticate_elasticsearch(cloud_id, api_key):
        set_session(True,
                    cloud_id=cloud_id,
                    api_key=api_key)
        st.success("✅ Login successful!")
        st.rerun()
    else:
        st.error("❌ Invalid Cloud ID or API Key")

if st.button("Logout"):
    logout()
