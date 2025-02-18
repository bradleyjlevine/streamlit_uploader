import streamlit as st
import pandas as pd
from utils.elastic import fetch_index_data, delete_document, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_delete():
    """Delete documents from Elasticsearch with data preview."""
    st.set_page_config(layout="wide")
    st.title("🗑️ Delete Documents")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    del st.session_state["delete_df"]

    # Fetch available indices
    indices = list_uploaded_files()
    index_names = [file["File Name"] for file in indices]

    if not index_names:
        st.info("No indices available. Upload a file first.")
        return

    selected_index = st.selectbox("Select an index to delete documents from", index_names)

    if st.button("Load Data"):
        data = fetch_index_data(selected_index, size=10)  # Fetch a preview of documents
        if data:
            df = pd.DataFrame(data)
            if "_id" not in df.columns:
                st.error("Missing `_id` field. Cannot delete documents without `_id`.")
                return
            st.session_state["delete_df"] = df.copy()

    if "delete_df" not in st.session_state:
        return

    df = st.session_state["delete_df"]

    st.subheader("📄 Existing Documents")
    st.dataframe(df, use_container_width=True)

    # Multi-select for deletion
    selected_rows = st.multiselect("Select documents to delete", df["_id"].tolist())

    if st.button("🗑️ Confirm Delete"):
        if selected_rows:
            for doc_id in selected_rows:
                delete_document(selected_index, doc_id)
            st.success(f"✅ Deleted {len(selected_rows)} document(s).")
            st.session_state["delete_df"] = df[~df["_id"].isin(selected_rows)]  # Remove from UI
        else:
            st.warning("No documents selected for deletion.")

if __name__ == "__main__":
    show_delete()
