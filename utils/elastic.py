import elasticsearch
from elasticsearch import helpers
import streamlit as st
import json, os, uuid

def list_uploaded_files():
    """Fetches a list of uploaded files and their corresponding indices."""
    cloud_id = st.session_state.get("cloud_id")
    api_key = st.session_state.get("api_key")

    es = elasticsearch.Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key,
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    with open(os.path.join(os.getcwd(),"config.json"), 'r') as f:
        config = json.load(f)

    index_pattern = config["index_pattern"] if "index_pattern" in config else "file-uploads."

    try:
        response = es.cat.indices(index=index_pattern + "*",v=True, format="json")
        indices = response.body
        return [{"File Name": idx["index"], "Docs Count": int(idx["docs.count"])} for idx in indices]
    except Exception as e:
        st.error(f"Error fetching uploaded files: {e}")
        return []

def fetch_index_data(index_name, lucene_query=None, size=1000):
    """Fetch documents from a specific index in Elasticsearch."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return []

    cloud_id = st.session_state["cloud_id"]
    api_key = st.session_state["api_key"]

    # Initialize Elasticsearch client
    es = elasticsearch.Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key,
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    try:

        if lucene_query:
            response = es.search(index=index_name, q=lucene_query, size=size)
        else:
            response = es.search(index=index_name, size=size)

        if "hits" in response and "hits" in response["hits"]:
            data = []
            for hit in response["hits"]["hits"]:
                row = {
                    "_id": hit["_id"]
                }
                row.update(hit["_source"])
                data.append(row)

            return data
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

def update_document(index_name, doc_id, updated_fields):
    """Applies a partial update to a document in Elasticsearch."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return

    es = elasticsearch.Elasticsearch(
        cloud_id=st.session_state["cloud_id"],
        api_key=st.session_state["api_key"],
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    try:
        del updated_fields["_id"]  # Remove the _id field from the update request

        response = es.update(
            index=index_name,
            id=doc_id,
            body={"doc": updated_fields}
        )
        if response.get("result") == "updated":
            st.success(f"✅ Document {doc_id} updated successfully.")
    except Exception as e:
        st.error(f"Error updating document {doc_id}: {str(e)}")

def add_new_document(index_name, doc_id, new_doc):
    """Adds a new document to Elasticsearch."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return

    es = elasticsearch.Elasticsearch(
        cloud_id=st.session_state["cloud_id"],
        api_key=st.session_state["api_key"],
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    try:
        del new_doc["_id"]  # Remove the ID field before indexing
        response = es.index(index=index_name, id=doc_id, body=new_doc)
        if response.get("result") == "created":
            st.success(f"✅ New document {doc_id} added successfully!")
    except Exception as e:
        st.error(f"Error adding document: {str(e)}")


def delete_document(index_name, doc_id):
    """Deletes a document from Elasticsearch."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return

    es = elasticsearch.Elasticsearch(
        cloud_id=st.session_state["cloud_id"],
        api_key=st.session_state["api_key"],
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    try:
        response = es.delete(index=index_name, id=doc_id)
        if response.get("result") == "deleted":
            st.success(f"✅ Document {doc_id} deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting document {doc_id}: {str(e)}")

def fetch_full_index(index_name, lucene_query=None, batch_size=500):
    """Fetch all documents from an Elasticsearch index using the Scroll API."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return []

    es = elasticsearch.Elasticsearch(
        cloud_id=st.session_state["cloud_id"],
        api_key=st.session_state["api_key"],
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    try:
        # Initialize scrolling
        if lucene_query:
            response = es.search(index=index_name, scroll="2m", q=lucene_query, size=batch_size)
        else:
            response = es.search(index=index_name, scroll="2m", size=batch_size, body={"query": {"match_all": {}}})

        documents = []

        for doc in response["hits"]["hits"]:
            row = {
                "_id": doc["_id"],
                "_op_type": "update"
            }
            row.update(doc["_source"])
            documents.append(row)

        # Scroll ID
        scroll_id = response["_scroll_id"]

        while len(response["hits"]["hits"]) > 0:
            response = es.scroll(scroll_id=scroll_id, scroll="2m")
            for doc in response["hits"]["hits"]:
                row = {
                    "_id": doc["_id"],
                    "_op_type": "update"
                }
                row.update(doc["_source"])
                documents.append(row)

        # Clear the scroll context
        es.clear_scroll(scroll_id=scroll_id)

        return documents
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return []
    
def bulk_update_documents(index_name, df):
    """Perform bulk updates in Elasticsearch using `_id` and `_op_type` from a CSV file."""
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Not authenticated. Please log in first.")
        return 0, 0

    es = elasticsearch.Elasticsearch(
        cloud_id=st.session_state["cloud_id"],
        api_key=st.session_state["api_key"],
        verify_certs=True,
        request_timeout=60,
        max_retries=3,
        retry_on_status=[429],
        http_compress=True
    )

    actions = []
    
    for _, row in df.iterrows():
        action = {"_op_type": row["_op_type"], "_index": index_name, "_id": row["_id"]}

        if row["_op_type"] in ["index"]:
            action["_source"] = row.drop(["_id", "_op_type"]).to_dict()
        elif row["_op_type"] == "update":
            action["doc"] = row.drop(["_id", "_op_type"]).to_dict()


        actions.append(action)

    try:
        success, failed = helpers.bulk(es, actions)
        return success, failed
    except Exception as e:
        st.error(f"Error executing bulk update: {str(e)}")
        return 0, len(actions)
    
def list_enrich_policies():

    es = elasticsearch.Elasticsearch(
    cloud_id=st.session_state["cloud_id"],
    api_key=st.session_state["api_key"],
    verify_certs=True,
    request_timeout=60,
    max_retries=3,
    retry_on_status=[429],
    http_compress=True)

    response = es.enrich.get_policy()

    if "policies" in response and len(response["policies"]) > 0:
        st.success("Enrich policies retrieved successfully")
    
        policies= []

        for policy in response["policies"]:
            policies.append({
                "name": policy["config"][list(policy["config"].keys())[0]]["name"],
                "type": list(policy["config"].keys())[0],
                "indices": policy["config"][list(policy["config"].keys())[0]]["indices"],
                "match_field":  policy["config"][list(policy["config"].keys())[0]]["match_field"],
                "enrich_fields": policy["config"][list(policy["config"].keys())[0]]["enrich_fields"]})

        return policies
    else:
        st.error("No policies found")
        return None

