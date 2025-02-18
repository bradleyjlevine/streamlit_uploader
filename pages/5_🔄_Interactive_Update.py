import streamlit as st
import pandas as pd
import uuid
from utils.elastic import fetch_index_data, update_document, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_edit():
    """Minimal interactive editor for updating Elasticsearch data."""
    st.set_page_config(layout="wide")
    st.title("✏️ Edit Data")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    del st.session_state["data_df"]

    # Fetch available indices
    indices = list_uploaded_files()
    index_names = [file["File Name"] for file in indices]

    if not index_names:
        st.info("No files found in Elasticsearch.")
        return

    # Select index
    selected_index = st.selectbox("Select a file to edit", index_names)

    # User can optionally specify a Lucene query
    st.subheader("🔍 Optional Lucene Query")
    lucene_query = st.text_area("Enter a Lucene query to filter documents (leave empty for all)", "")

    if st.button("🔄 Load Data"):
        data = fetch_index_data(selected_index, lucene_query=lucene_query)
        if data:
            df = pd.DataFrame(data)
            if "_id" not in df.columns:
                st.error("Missing `_id` field. Cannot edit documents without `_id`.")
                return
            st.session_state["data_df"] = df.copy()

    if "data_df" not in st.session_state:
        return

    df = st.session_state["data_df"]
    edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed")

    # Ensure column order matches before comparison
    edited_df = edited_df[df.columns]

    if st.button("💾 Save Changes"):
        changes = df.compare(edited_df, keep_shape=True, keep_equal=False)

        if not changes.empty:
            for idx in changes.index.unique():
                doc_id = edited_df.loc[idx, "_id"]
                updated_fields = edited_df.loc[idx].to_dict()
                update_document(selected_index, doc_id, updated_fields)

        st.session_state["data_df"] = edited_df.copy()
        st.success("✅ Changes saved successfully!")

if __name__ == "__main__":
    show_edit()