import streamlit as st
import pandas as pd
from utils.elastic import fetch_index_data, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_view():
    """Fetch and display uploaded files from Elasticsearch with pagination."""
    st.set_page_config(layout="wide")
    st.title("📄 View Uploaded File")

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
        st.info("No files found in Elasticsearch.")
        return

    # Select index
    selected_index = st.selectbox("Select a file to view", index_names)

    # User can optionally specify a Lucene query
    st.subheader("🔍 Optional Lucene Query")
    lucene_query = st.text_area("Enter a Lucene query to filter documents (leave empty for all)", "")

    # Store pagination settings in session state
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    if "page_size" not in st.session_state:
        st.session_state.page_size = 10

    # Row selection per page
    st.session_state.page_size = st.selectbox("Rows per page", [10, 20, 50, 100], index=0)

    if st.button("🔄 Load Data"):
        data = fetch_index_data(selected_index, lucene_query)

        if data:
            st.session_state["view_df"] = pd.DataFrame(data)
            st.session_state.page_number = 1  # Reset to page 1 after loading new data

    if "view_df" not in st.session_state:
        return

    df = st.session_state["view_df"]

    # Pagination logic
    total_pages = (len(df) // st.session_state.page_size) + 1
    st.session_state.page_number = st.number_input("Page number", min_value=1, max_value=total_pages, value=st.session_state.page_number)

    # Compute start and end indices for pagination
    start_idx = (st.session_state.page_number - 1) * st.session_state.page_size
    end_idx = start_idx + st.session_state.page_size

    # Display paginated data
    st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)

if __name__ == "__main__":
    show_view()
