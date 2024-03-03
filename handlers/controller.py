import pykube
from config import EnvConfig
from constants import NAME_SELECTOR
from custom_resources import GatewayResource, VirtualServiceResource
from schemas import (
    DeployConfig,
    ServiceConfig,
    VirtualServiceConfig,
)


class KubernetesController:
    def __init__(self) -> None:
        if EnvConfig.ENV in ["dev", "test"]:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_file("config.yml"))
        else:
            self.api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())

    def get_api(self):
        return self.api

    def create_deployment(self, deploy_config: DeployConfig):
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
                        "imagePullSecrets": deploy_config.imagePullSecrets,
                        "containers": deploy_config.containers,
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
                "ports": service_config.ports,
                "selector": service_config.labels,
                "type": service_config.type,
            },
        }

    def create_virtual_service(self, virtual_service_config: VirtualServiceConfig):

        virtual_service = {
            "apiVersion": "networking.istio.io/v1alpha3",
            "kind": "VirtualService",
            "metadata": {
                "labels": virtual_service_config.labels,
            },
            "spec": {
                "hosts": ["*"],
                "gateways": [virtual_service_config.gateway],
            },
        }
        for container in virtual_service_config.containers_configs:
            if container.path:
                virtual_service["spec"]["http"] = [
                    {
                        "match": [
                            {
                                "uri": {
                                    "prefix": virtual_service_config.path,
                                }
                            }
                        ],
                        "route": [
                            {
                                "destination": {
                                    "host": container.name,
                                    "port": {"number": container.port["containerPort"]},
                                }
                            }
                        ],
                        "timeout": virtual_service_config.timeout,
                    }
                ]

    def update_deployment(self, deploy_config: DeployConfig):
        deployment = self.get_deployment_by_name(
            deploy_config.name, deploy_config.namespace
        )
        deployment.obj["spec"]["replicas"] = deploy_config.replicas
        deployment.obj["spec"]["template"]["spec"][
            "containers"
        ] = deploy_config.containers
        deployment.obj["spec"]["template"]["spec"][
            "imagePullSecrets"
        ] = deploy_config.imagePullSecrets
        deployment.update()
        return deployment

    def update_service(self, service_config: ServiceConfig):
        service = self.get_service_by_name(
            service_config.name, service_config.namespace
        )
        service.obj["spec"]["ports"][0]["port"] = service_config.port
        service.obj["spec"]["ports"][0]["targetPort"] = service_config.port
        service.update()
        return service

    def update_virtual_service(self, virtual_service_config: VirtualServiceConfig):
        if not (
            virtual_service := self.get_virtual_service_by_name(
                virtual_service_config.name,
                namespace=virtual_service_config.namespace,
            )
        ):
            return self.create_virtual_service(virtual_service_config), False
        virtual_service.obj["spec"]["gateways"] = [virtual_service_config.gateway]
        virtual_service.obj["spec"]["http"][0]["match"][0]["uri"][
            "prefix"
        ] = virtual_service_config.path
        virtual_service.obj["spec"]["http"][0]["route"][0]["destination"]["port"][
            "number"
        ] = virtual_service_config.port
        virtual_service.obj["spec"]["http"][0][
            "timeout"
        ] = virtual_service_config.timeout
        virtual_service.update()
        return virtual_service, True

    def get_deployment_by_labels(self, labels: dict, namespace):
        deployments = pykube.Deployment.objects(self.api).filter(
            selector=labels, namespace=namespace
        )
        for deployment in deployments:
            return deployment

    def get_deployment_by_name(self, name: str, namespace: str):
        deployments = pykube.Deployment.objects(self.api).filter(
            field_selector={NAME_SELECTOR: name}, namespace=namespace
        )
        for deployment in deployments:
            return deployment

    def get_service_by_labels(self, labels: dict, namespace):
        services = pykube.Service.objects(self.api).filter(
            namespace=namespace, selector=labels
        )
        for service in services:
            return service

    def get_service_by_name(self, name: str, namespace: str):
        services = pykube.Service.objects(self.api).filter(
            field_selector={NAME_SELECTOR: name}, namespace=namespace
        )
        for service in services:
            return service

    def get_virtual_service_by_labels(self, labels: dict, namespace: str):
        virtual_services = VirtualServiceResource.objects(self.api).filter(
            selector=labels, namespace=namespace
        )
        for virtual_service in virtual_services:
            return virtual_service

    def get_virtual_service_by_name(self, name: str, namespace: str):
        virtual_services = VirtualServiceResource.objects(self.api).filter(
            field_selector={NAME_SELECTOR: name}, namespace=namespace
        )
        for virtual_service in virtual_services:
            return virtual_service

    def get_gateway_by_name(self, name: str, namespace):
        gateways = GatewayResource.objects(self.api).filter(
            field_selector={NAME_SELECTOR: name}, namespace=namespace
        )
        for gateway in gateways:
            return gateway

    def create_gateway(self, gateway_config: dict):
        gateway = GatewayResource(self.api, gateway_config)
        gateway.create()
        return gateway
