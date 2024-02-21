import pykube
from config import EnvConfig
from schemas import (
    DeployConfig,
    ServiceConfig,
)


class KubernetesController:
    def __init__(self) -> None:
        if EnvConfig.ENV in ["dev", "test"]:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_file("config.yml"))
        else:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())

    def get_api(self):
        return self.api

    def create_deployment(self, deploy_config: DeployConfig, name: str):
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "labels": deploy_config.labels,
            },
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
                                "ports": [{"containerPort": deploy_config.port}],
                                "env": deploy_config.env,
                                "resources": {
                                    "limits": {
                                        "cpu": deploy_config.resources.cpu_limit,
                                        "memory": deploy_config.resources.memory_limit,
                                    },
                                    "requests": {
                                        "cpu": deploy_config.resources.cpu_request,
                                        "memory": deploy_config.resources.memory_request,
                                    },
                                },
                            }
                        ],
                    },
                },
            },
        }

    def create_service(self, service_config: ServiceConfig):
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "labels": service_config.labels,
            },
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

    def update_deployment(self, deploy_config: DeployConfig):
        deployment = self.get_deployment_by_labels(
            deploy_config.labels, namespace=deploy_config.namespace
        )
        deployment.obj["spec"]["replicas"] = deploy_config.replicas
        deployment.obj["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = deploy_config.image
        deployment.obj["spec"]["template"]["spec"]["containers"][0][
            "env"
        ] = deploy_config.env
        deployment.obj["spec"]["template"]["spec"]["containers"][0]["resources"] = {
            "limits": {
                "cpu": deploy_config.resources.cpu_limit,
                "memory": deploy_config.resources.memory_limit,
            },
            "requests": {
                "cpu": deploy_config.resources.cpu_request,
                "memory": deploy_config.resources.memory_request,
            },
        }
        deployment.update()
        return deployment

    def update_service(self, service_config: ServiceConfig):
        service = self.get_service_by_labels(
            service_config.labels, namespace=service_config.namespace
        )
        service.obj["spec"]["ports"][0]["port"] = service_config.port
        service.obj["spec"]["ports"][0]["targetPort"] = service_config.port
        service.update()
        return service

    def get_deployment_by_labels(self, labels: dict, namespace: str = "default"):
        deployments = pykube.Deployment.objects(self.api).filter(
            selector=labels, namespace=namespace
        )
        for deployment in deployments:
            return deployment

    def get_service_by_labels(self, labels: dict, namespace: str = "default"):
        services = pykube.Service.objects(self.api).filter(
            selector=labels, namespace=namespace
        )
        for service in services:
            return service
