from pykube.objects import NamespacedAPIObject


class GatewayResource(NamespacedAPIObject):
    """Gateway configuration."""

    version: str = "networking.istio.io/v1alpha3"
    endpoint: str = "gateways"
    kind: str = "Gateway"


class VirtualServiceResource(NamespacedAPIObject):
    """VirtualService configuration."""

    version: str = "networking.istio.io/v1alpha3"
    endpoint: str = "virtualservices"
    kind: str = "VirtualService"
