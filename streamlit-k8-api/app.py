from shiny import App, ui, reactive
from kubernetes import client, config

# Function to load in-cluster Kubernetes config
def load_incluster_config():
    try:
        config.load_incluster_config()
        return "Kubernetes in-cluster config loaded successfully."
    except Exception as e:
        return f"Error loading Kubernetes in-cluster config: {e}"

# Function to list pods across all namespaces
def list_all_pods():
    try:
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False)
        return pods.items
    except Exception as e:
        raise RuntimeError(f"Error fetching pods: {e}")

# UI definition
app_ui = ui.page_fluid(
    ui.h2("Kubernetes Pod Viewer"),
    ui.p("Displays all pods across all namespaces with their IPs."),
    ui.div(
        ui.output_text("config_status"),
        class_="config-status"
    ),
    ui.output_ui("pods_list"),
    ui.action_button("refresh", "Refresh Pods List")
)

# Server logic
def server(input, output, session):
    # Reactive value to store pods list
    pods_reactive = reactive.Value([])

    # Load Kubernetes config on startup
    config_status = load_incluster_config()

    @reactive.Effect
    @reactive.event(input.refresh)
    def refresh_pods():
        try:
            pods = list_all_pods()
            pods_reactive.set(pods)
        except Exception as e:
            pods_reactive.set([])
            session.toast(f"Error refreshing pods: {e}", duration=5, type="danger")

    # Render Kubernetes config load status
    @output
    @reactive.Effect
    def config_status():
        return config_status

    # Render the list of pods
    @output
    @reactive.Effect
    def pods_list():
        pods = pods_reactive()
        if not pods:
            return ui.div("No pods found or an error occurred.", class_="no-pods")

        pod_elements = []
        for pod in pods:
            pod_elements.append(
                ui.div(
                    ui.strong(f"Pod Name: {pod.metadata.name}"),
                    ui.div(f"Namespace: {pod.metadata.namespace}"),
                    ui.div(f"Pod IP: {pod.status.pod_ip}"),
                    class_="pod-item"
                )
            )
        return ui.div(*pod_elements, class_="pods-list")

# Create the app instance
app = App(app_ui, server)
