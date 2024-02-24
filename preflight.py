import logging

from handlers.controller import KubernetesController


gateway = {
    "apiVersion": "networking.istio.io/v1alpha3",
    "kind": "Gateway",
    "metadata": {
        "name": "microservice-gateway",
        "namespace": "istio-system",
    },
    "spec": {
        "selector": {
            "istio": "ingressgateway",
        },
        "servers": [
            {
                "port": {
                    "number": 80,
                    "name": "http",
                    "protocol": "HTTP",
                },
                "hosts": ["*"],
            }
        ],
    },
}


def run():
    try:
        kubernetes_controller = KubernetesController()
        if not kubernetes_controller.get_gateway_by_name(
            "microservice-gateway", "istio-system"
        ):
            kubernetes_controller.create_gateway(gateway)
            logging.info("Gateway created.")
        else:
            logging.info("Gateway already exists.")
    except Exception as e:
        logging.error(f"Error creating gateway: {e}")
        raise e
