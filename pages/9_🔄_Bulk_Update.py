import streamlit as st
import pandas as pd
from utils.elastic import bulk_update_documents, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_bulk_update():
    """Bulk update Elasticsearch documents using a CSV file."""
    st.set_page_config(layout="wide")
    st.title("📂 Bulk Update Documents")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    if "bulk_df" in st.session_state:
        del st.session_state["bulk_df"]

    # Fetch available indices
    indices = list_uploaded_files()
    index_names = [file["File Name"] for file in indices]

    if not index_names:
        st.info("No indices available. Upload a file first.")
        return

    selected_index = st.selectbox("Select an index to update", index_names)

    # File uploader
    uploaded_file = st.file_uploader("📤 Upload CSV file for bulk update", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Validate required fields
        if "_id" not in df.columns or "_op_type" not in df.columns:
            st.error("CSV file must contain `_id` and `_op_type` columns!")
            return

        st.session_state["bulk_df"] = df.copy()

        # Show preview
        st.subheader("📑 Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("🚀 Confirm & Execute Updates"):
            success, failed = bulk_update_documents(selected_index, df)

            st.success(f"✅ Successfully processed {success} operations!")
            if failed:
                st.error(f"⚠️ {failed} operations failed. Check Elasticsearch logs.")

if __name__ == "__main__":
    show_bulk_update()
