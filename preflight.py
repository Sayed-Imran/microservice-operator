import logging
from pykube.objects import NamespacedAPIObject

from handlers.py_kube_controller import KubernetesController

class GatewayResource(NamespacedAPIObject):
    """Gateway configuration."""

    version: str = "networking.istio.io/v1alpha3"
    endpoint: str = "gateways"
    kind: str = "Gateway"

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
try:
    kubernetes_controller = KubernetesController()
    api = kubernetes_controller.get_api()

    gateway_resource = GatewayResource(api, gateway)
    gateway_resource.create()
except Exception as e:
    logging.error(f"Error creating gateway: {e}")
    raise e