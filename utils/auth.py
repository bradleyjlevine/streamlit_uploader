import elasticsearch
import streamlit as st

def authenticate_elasticsearch(cloud_id: str, api_key: str) -> bool:
    """Authenticates Elasticsearch API key and returns True if valid."""

    # Create an Elasticsearch client using the provided credentials
    es = elasticsearch.Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key,
        verify_certs=True,
        request_timeout=30,
        max_retries=5,
        retry_on_status=[429],
        opaque_id="StreamlitESUploader-Auth"
    )
    
    try:
        response = es.count()
        return True
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return False
