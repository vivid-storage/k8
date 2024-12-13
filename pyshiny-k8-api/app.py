from kubernetes import client, config
from shiny import App, reactive, render, ui


# Load Kubernetes config
def load_incluster_config():
    try:
        config.load_incluster_config()
        return "Kubernetes config loaded successfully."
    except Exception as e:
        return f"Error loading Kubernetes config: {e}"


# List all pods
def list_all_pods():
    v1 = client.CoreV1Api()
    ret = v1.list_pod_for_all_namespaces(watch=False)
    return ret.items


# Shiny UI
app_ui = ui.page_fluid(
    ui.h2("Kubernetes Pods Viewer"),
    ui.output_text_verbatim("config_status"),
    ui.input_action_button("refresh", "Refresh Pods"),
    ui.output_text_verbatim("notification"),
    ui.output_ui("pods_list"),
)


# Server logic
def server(input, output, session):
    # Reactive value to store the list of pods
    pods_reactive = reactive.Value([])

    # Reactive value to store notification messages
    notification_message = reactive.Value("")

    # Load Kubernetes config on startup
    config_status_message = load_incluster_config()

    @reactive.Effect
    @reactive.event(input.refresh)
    def refresh_pods():
        try:
            pods = list_all_pods()
            pods_reactive.set(pods)
            notification_message.set("Pods refreshed successfully!")
        except Exception as e:
            pods_reactive.set([])
            notification_message.set(f"Error refreshing pods: {e}")

    # Render Kubernetes config load status
    @output
    @render.text
    def config_status():
        return config_status_message

    # Render notification messages
    @output
    @render.text
    def notification():
        return notification_message()

    # Render the list of pods
    @output
    @render.ui
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


# Create the app
app = App(app_ui, server)
