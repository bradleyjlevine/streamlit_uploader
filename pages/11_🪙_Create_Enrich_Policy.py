import streamlit as st
from utils.session import get_session, logout, is_session_expired
from utils.elastic import create_enrich_policy as cep, execute_enrich_policy

def create_enrich_policy():
    """Bulk update Elasticsearch documents using a CSV file."""
    st.set_page_config(layout="wide")
    st.title("🪙 Create Enrich Policy")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    enrich_policy_name = st.text_input("Enter Enrich Policy Name:", )
    enrich_policy_type = st.selectbox("Select Enrich Policy Type:", ["match", "range"])
    enrich_policy_indices = st.text_input("Enter Indexes (comma-separated):")
    enrich_policy_match_field = st.text_input("Match Field:")
    enrich_policy_enrich_fields = st.text_input("Enrich Fields (comma-separated):")

    if st.button("Create Enrich Policy"):
        if not (enrich_policy_name and enrich_policy_type and enrich_policy_indices and enrich_policy_match_field and enrich_policy_enrich_fields):
            st.error("All fields are required.")
        else:
            if cep(enrich_policy_name, enrich_policy_type, enrich_policy_indices, enrich_policy_match_field, enrich_policy_enrich_fields):
                st.success("Enrich Policy created successfully.")
                execute_enrich_policy(enrich_policy_name)
            else:
                st.error(f"Failed to create Enrich Policy '{enrich_policy_name}'")


if __name__ == "__main__":
    create_enrich_policy()