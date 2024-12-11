import streamlit as st
from kubernetes import client, config

# Function to load in-cluster Kubernetes config
def load_incluster_config():
    try:
        config.load_incluster_config()
        st.success("Kubernetes in-cluster config loaded successfully.")
    except Exception as e:
        st.error(f"Error loading Kubernetes in-cluster config: {e}")


# Function to list pods across all namespaces
def list_all_pods():
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    return pods.items


# Function to display pods in the Streamlit app
def display_pods(pods):
    if pods:
        st.subheader("Pods List")
        for pod in pods:
            st.write(
                f"**Pod Name**: {pod.metadata.name}, "
                f"**Namespace**: {pod.metadata.namespace}, "
                f"**Pod IP**: {pod.status.pod_ip}"
            )
    else:
        st.info("No pods found.")


# Streamlit UI
st.title("Kubernetes Pod Viewer")
st.markdown("Displays all pods across all namespaces with their IPs.")

# Load Kubernetes config
load_incluster_config()

# Try to list pods when the app starts
try:
    initial_pods = list_all_pods()
    st.info("Automatically listing all pods on startup...")
    display_pods(initial_pods)
except Exception as e:
    st.error(f"Error fetching pods on startup: {e}")

# Button to manually refresh pod list
if st.button("Refresh Pods List"):
    try:
        st.info("Refreshing pod list...")
        refreshed_pods = list_all_pods()
        display_pods(refreshed_pods)
    except Exception as e:
        st.error(f"Error refreshing pods: {e}")
