import pykube
from config import EnvConfig
from schemas import DeployConfig, ServiceConfig
import yaml

class KubernetesController:
    def __init__(self) -> None:
        if EnvConfig.env == 'local':
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_file(EnvConfig.KUBECONFIG_PATH))
        else:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())
    
    def get_api(self):
        return self.api

    def create_deployment(self, deploy_config: DeployConfig):
        deploy_config.env = {key: str(value) for key, value in deploy_config.env.items()}
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
                                "name": deploy_config.name,
                                "image": deploy_config.image,
                                "env": [
                                    {
                                        "name": key,
                                        "value": value
                                    }
                                    for key, value in deploy_config.env.items()
                                ],
                                "ports": [
                                    {
                                        "containerPort": deploy_config.port
                                    }
                                ],
                                "resources": {
                                    "limits": deploy_config.resources,
                                    "requests": deploy_config.resources,
                                },
                            }
                        ],
                        "nodeSelector": deploy_config.node_selector,
                        "affinity": deploy_config.affinity,
                        "tolerations": deploy_config.tolerations,
                        "serviceAccount": deploy_config.service_account,
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
                        "name": service_config.name,
                        "port": service_config.port,
                        "targetPort": service_config.port,
                    }
                ],
                "selector": service_config.labels,
            },
        }
        return yaml.safe_load(yaml.dump(service))
