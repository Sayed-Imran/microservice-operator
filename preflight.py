import logging

from handlers.kube_handler import KubernetesHandler


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
        kubernetes_handler = KubernetesHandler()
        if not kubernetes_handler.get_gateway_by_name(
            "microservice-gateway", "istio-system"
        ):
            kubernetes_handler.create_gateway(gateway)
            logging.info("Gateway created.")
        else:
            logging.info("Gateway already exists.")
    except Exception as e:
        logging.error(f"Error creating gateway: {e}")
        raise e
