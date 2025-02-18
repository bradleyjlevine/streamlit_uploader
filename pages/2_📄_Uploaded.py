import streamlit as st
from utils.elastic import list_uploaded_files
from utils.session import get_session, logout, is_session_expired
import pandas as pd

def show_file_list():
    """Displays a list of uploaded files and their corresponding indices."""
    st.set_page_config(layout="wide")
    
    st.title("📂 Uploaded Files")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    files = list_uploaded_files()
    
    if not files:
        st.info("No files have been uploaded yet.")
        return

    df = pd.DataFrame(files)
    st.dataframe(df, use_container_width=True)


# Load the page
if __name__ == "__main__":
    show_file_list()
