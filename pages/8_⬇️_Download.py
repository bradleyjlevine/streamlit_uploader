import streamlit as st
import pandas as pd
import json
from utils.elastic import fetch_full_index, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_download():
    """Download full Elasticsearch indices."""
    st.set_page_config(layout="wide")
    st.title("📥 Download Full Index")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    # Fetch available indices
    indices = list_uploaded_files()
    index_names = [file["File Name"] for file in indices]

    if not index_names:
        st.info("No indices available. Upload a file first.")
        return

    selected_index = st.selectbox("Select an index to download", index_names)

    # User can optionally specify a Lucene query
    st.subheader("🔍 Optional Lucene Query")
    lucene_query = st.text_area("Enter a Lucene query to filter documents (leave empty for all)", "")

    if st.button("🔄 Fetch Data"):
        data = fetch_full_index(selected_index, lucene_query)

        if data:
            df = pd.DataFrame(data)
            st.session_state["download_df"] = df.copy()
            st.success(f"✅ Retrieved {len(df)} documents from `{selected_index}`.")

    if "download_df" not in st.session_state:
        return

    df = st.session_state["download_df"]

    # Display preview
    st.subheader("📄 Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    # Provide download options
    st.subheader("📥 Download Options")

    csv = df.to_csv(index=False).encode("utf-8")
    json_data = df.to_json(orient="records", indent=2)

    st.download_button(
        label="📄 Download as CSV",
        data=csv,
        file_name=f"{selected_index}.csv",
        mime="text/csv",
    )

    st.download_button(
        label="📄 Download as JSON",
        data=json_data,
        file_name=f"{selected_index}.json",
        mime="application/json",
    )

if __name__ == "__main__":
    show_download()
