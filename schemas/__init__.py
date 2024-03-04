from typing import Any
from pydantic import BaseModel


class Resource(BaseModel):
    """Resource configuration."""

    cpu_limit: str = "100m"
    cpu_request: str = "100m"
    memory_limit: str = "128Mi"
    memory_request: str = "128Mi"


class ContainerConfig(BaseModel):
    """Container configuration."""

    name: str
    image: str
    imagePullPolicy: str = "ifNotPresent"
    ports: list[dict[str, Any]] = [{"containerPort": 80}]
    path: str | None = None
    env: list[dict[str, Any]] = []
    resources: Resource | dict = Resource().model_dump()
    livenessProbe: dict[str, Any] | None = None
    readinessProbe: dict[str, Any] | None = None
    volumeMounts: list[dict[str, Any]] = []
    command: list[str] = []


class DeployConfig(BaseModel):
    """Deploy configuration."""

    name: str
    imagePullSecrets: list[str] = []
    namespace: str = "default"
    replicas: int = 1
    labels: dict[str, str] = {}
    annotations: dict[str, str] = {}
    affinity: dict[str, str] = {}
    tolerations: dict[str, str] = {}
    serviceAccount: str | None = None
    containers: list[ContainerConfig]
    volumes: list[dict[str, Any]] = []


class ServiceConfig(BaseModel):
    """Service configuration."""

    name: str
    namespace: str = "default"
    containers: list[ContainerConfig]
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
    containers_configs: list[ContainerConfig]
    timeout: str = "5s"
