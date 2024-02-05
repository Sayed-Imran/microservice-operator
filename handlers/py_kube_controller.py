import pykube
from config import EnvConfig
from schemas import DeployConfig, ServiceConfig
import yaml

class KubernetesController:
    def __init__(self) -> None:
        if EnvConfig.ENV in ['dev', 'test']:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_file("config.yml"))
        else:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())

    def get_api(self):
        return self.api

    def create_deployment(self, deploy_config: DeployConfig, name: str):
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "spec": {
                "replicas": deploy_config.replicas,
                "selector": {
                    "matchLabels": deploy_config.labels,
                },
                "template": {
                    "metadata": {
                        "labels": deploy_config.labels,
                        "annotations": deploy_config.annotations,
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": name,
                                "image": deploy_config.image,
                                "ports": [
                                    {
                                        "containerPort": deploy_config.port
                                    }
                                ],
                                "env": deploy_config.env,
                                "resources": {
                                    "limits": {
                                        "cpu": deploy_config.resources.cpu_limit,
                                        "memory": deploy_config.resources.memory_limit,},
                                    "requests": {
                                        "cpu": deploy_config.resources.cpu_request,
                                        "memory": deploy_config.resources.memory_request},
                                },
                            }
                        ],
                    },
                },
            },
        }

        return yaml.safe_load(yaml.dump(deployment))


    def create_service(self, service_config: ServiceConfig):
        service = {
            "apiVersion": "v1",
            "kind": "Service",
    
            "spec": {
                "ports": [
                    {
                        "name": "port",
                        "port": service_config.port,
                        "targetPort": service_config.port,
                    }
                ],
                "selector": service_config.labels,
                "type": service_config.type,
            },
        }
        return yaml.safe_load(yaml.dump(service))
