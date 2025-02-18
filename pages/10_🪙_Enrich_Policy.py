import streamlit as st
import pandas as pd
from utils.session import get_session, logout, is_session_expired
from utils.elastic import list_enrich_policies


def show_enrich_policy():
    """Bulk update Elasticsearch documents using a CSV file."""
    st.set_page_config(layout="wide")
    st.title("Enrich Policy")

    session = get_session()

    if not session["authenticated"]:
        st.warning("Please log in first.")
        st.stop()

    if is_session_expired():
        logout()

    if st.button("Get Policies"):
        policies = list_enrich_policies()
        if policies:
            df = pd.DataFrame(policies)
            st.dataframe(df,  use_container_width=True)

if __name__ == "__main__":
    show_enrich_policy()