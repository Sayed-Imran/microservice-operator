from typing import Literal
from pydantic_settings import BaseSettings
from errors import KubeConfigError
from kubernetes import client, config
from dotenv import load_dotenv
load_dotenv()

class _EnvConfig(BaseSettings):
    """Base configuration."""
    ENV: Literal["dev", "test", "prod"] = "dev"
    KUBECONFIG_PATH: str | None = None



EnvConfig = _EnvConfig()

if EnvConfig.ENV == "dev":
    if not EnvConfig.KUBECONFIG_PATH:
        raise KubeConfigError("KUBECONFIG_PATH not set")
    else:
        config.load_kube_config(EnvConfig.KUBECONFIG_PATH)

else:
    config.load_incluster_config()

api_client = client.ApiClient()
apps_v1 = client.AppsV1Api(api_client)
core_v1 = client.CoreV1Api(api_client)

