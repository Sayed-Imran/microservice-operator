from typing import Any
from pydantic import BaseModel


class Resource(BaseModel):
    """Resource configuration."""

    cpu_limit: str = "100m"
    cpu_request: str = "100m"
    memory_limit: str = "128Mi"
    memory_request: str = "128Mi"


class DeployConfig(BaseModel):
    """Deploy configuration."""

    name: str
    image: str
    namespace: str = "default"
    replicas: int = 1
    labels: dict[str, Any]
    port: int = 80
    path: str = "/"
    env: list[dict[str, Any]] = []
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}
    resources: Resource | dict = Resource().model_dump()
    node_selector: dict[str, str] = {}
    affinity: dict[str, str] = {}
    tolerations: dict[str, str] = {}
    service_account: str | None = None


class ServiceConfig(BaseModel):
    """Service configuration."""

    name: str
    namespace: str = "default"
    port: int = 80
    type: str = "ClusterIP"
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}


class VirtualServiceConfig(BaseModel):
    """VirtualService configuration."""

    name: str
    labels: dict[str, str] = {}
    host: str = ""
    gateway: str = "istio-system/microservice-gateway"
    namespace: str = "default"
    path: str = "/"
    timeout: str = "5s"
    port: int = 80
