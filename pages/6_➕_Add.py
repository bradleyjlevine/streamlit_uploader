import streamlit as st
import pandas as pd
import uuid
from utils.elastic import fetch_index_data, add_new_document, list_uploaded_files
from utils.session import get_session, logout, is_session_expired

def show_add():
    """Add new documents to Elasticsearch with suggested fields."""
    st.title("➕ Add New Documents")

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

    selected_index = st.selectbox("Select an index to add documents", index_names)

    st.subheader("📋 Sample Document Fields")

    # Fetch sample documents to determine the fields
    sample_data = fetch_index_data(selected_index, size=3)  # Fetch 3 sample docs
    field_names = set()
    
    if sample_data:
        sample_df = pd.DataFrame(sample_data)
        field_names = set(sample_df.columns) - {"_id"}  # Exclude `_id`
        st.write("💡 Based on existing documents, these are the expected fields:")
        st.dataframe(sample_df.head(), use_container_width=True)
    else:
        st.warning("No sample documents found. You will need to manually enter fields.")

    st.subheader("✏️ Enter Document Data")

    # Allow users to input values for each field
    new_doc = {}
    for field in field_names:
        new_doc[field] = st.text_input(f"{field}", "")

    # Allow users to add custom fields
    st.subheader("➕ Add Custom Fields")
    custom_field_name = st.text_input("New Field Name", "")
    custom_field_value = st.text_input("New Field Value", "")

    if st.button("➕ Add Column"):
        if custom_field_name:
            new_doc[custom_field_name] = custom_field_value
            st.success(f"✅ Field `{custom_field_name}` added!")
        else:
            st.warning("Column name cannot be empty!")

    # Store new documents in session state for batch addition
    if "new_docs" not in st.session_state:
        st.session_state["new_docs"] = []

    if st.button("📌 Add to Batch"):
        if new_doc:
            new_doc["_id"] = str(uuid.uuid4())  # Generate unique ID
            st.session_state["new_docs"].append(new_doc)
            st.success(f"✅ Document added to batch with ID `{new_doc['_id']}`")
        else:
            st.warning("No data entered!")

    # Show all new documents before submission
    if st.session_state["new_docs"]:
        st.subheader("📑 Documents Ready to Upload")
        st.dataframe(pd.DataFrame(st.session_state["new_docs"]), use_container_width=True)

        if st.button("🚀 Upload to Elasticsearch"):
            for doc in st.session_state["new_docs"]:
                add_new_document(selected_index, doc["_id"], doc)
            st.session_state["new_docs"] = []
            st.success("✅ All documents uploaded successfully!")

if __name__ == "__main__":
    show_add()
