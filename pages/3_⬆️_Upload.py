import streamlit as st
import pandas as pd
from utils.file_handler import process_csv_upload
from utils.session import get_session, logout, is_session_expired

def show_upload():
    """Handles CSV file uploads with optional type overrides."""
    st.title("📤 Upload CSV File")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### File Preview")
        st.dataframe(df.head(), use_container_width=True)

        # Allow user to choose whether to override column types
        override_types = st.checkbox("Override Column Types?")

        column_types = {}
        if override_types:
            st.write("### Column Type Overrides")
            for col in df.columns:
                column_types[col] = st.selectbox(f"Column Type for {col}", ["string", "integer", "float"], key=col)

        if st.button("Confirm & Upload"):
            process_csv_upload(uploaded_file, column_types if override_types else None)
            st.success("✅ File uploaded successfully!")

# Load the page
if __name__ == "__main__":
    show_upload()
