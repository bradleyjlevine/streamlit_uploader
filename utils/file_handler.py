import streamlit as st
import pandas as pd
from elasticsearch import Elasticsearch, helpers
import json, os, uuid

def process_csv_upload(file, column_types=None):
    """Handles CSV upload and sends data to Elasticsearch using the bulk helper."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return
    
    cloud_id = st.session_state["cloud_id"]
    api_key = st.session_state["api_key"]

    with open(os.path.join(os.getcwd(),"config.json"), 'r') as f:
        config = json.load(f)

    index_pattern = config["index_pattern"] if "index_pattern" in config else "file-uploads."

    # Initialize Elasticsearch client
    es = Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key
    )

    file.seek(0)  # Reset the file pointer to the beginning of the uploaded file

    df = pd.read_csv(file)

    # Apply column type overrides only if specified
    if column_types:
        for col, dtype in column_types.items():
            if dtype == "integer":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            elif dtype == "float":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
            else:
                df[col] = df[col].astype(str)

    index_name = index_pattern + file.name.replace(".csv", "").lower().replace(" ", "_").replace("-", "_") + "-prod"
    

    def gendata(data: list):
        for item in data:
           yield {
               "_id":  uuid.uuid4(),
                "_op_type": "index",
                "_index": index_name,
                "_source": item
           }

    # Execute bulk upload
    success, failed = helpers.bulk(es, gendata(df.to_dict(orient="records")))

    if len(failed) == 0:
        st.success(f"✅ Successfully uploaded {success} documents to '{index_name}' using Bulk API!")
    else:
        st.error(f"⚠️ Uploaded {success} documents, but {failed} failed. Check Elasticsearch logs for details.")
