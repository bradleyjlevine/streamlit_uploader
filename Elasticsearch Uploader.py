import streamlit as st
from utils.session import get_session, logout, is_session_expired

st.set_page_config(
    page_title="Elasticsearch Uploader",
    page_icon=":Elasticsearch:",
    layout="wide"
)

st.write("# Welcome to the Elasticsearch Uploader")

st.markdown(
    """
    This app allows you to upload files to an Elasticsearch server using Streamlit and the `elasticsearch` library.
    """
)

session = get_session()

if not session["authenticated"]:
    st.warning("Please log in first.")
    st.stop()

if is_session_expired():
    logout()
