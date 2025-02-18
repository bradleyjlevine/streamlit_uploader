import streamlit as st
from utils.session import get_session, logout, is_session_expired
from utils.elastic import list_enrich_policies, execute_enrich_policy as eep

def execute_enrich_policy():
    """Bulk update Elasticsearch documents using a CSV file."""
    st.set_page_config(layout="wide")
    st.title("🪙 Execute Enrich Policy")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    policies = list_enrich_policies()
    if policies:
        policy_name = st.selectbox("Select a policy to execute:", [policy["name"] for policy in policies])

        if policy_name:
            if st.button("Execute Policy"):
                eep(policy_name)

if __name__ == "__main__":
    execute_enrich_policy()
