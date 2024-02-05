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
    image: str
    replicas: int = 1
    labels: dict[str, Any]
    port: int = 80
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
    port: int = 80
    type: str = "ClusterIP"
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}

class VirtualServiceConfig(BaseModel):
    """Virtual Service configuration."""
    name: str
    host: str
    port: int = 80
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}
    gateways: list[str] = []
    http: list[dict[str, Any]] = []
    tcp: list[dict[str, Any]] = []
    path: str = "/"
    service: str = ""
    rewrite: str = ""