from kubernetes import client
from schemas import DeployConfig


class KubernetesController:
    def create_deployment(self, deploy_config: DeployConfig, apps_v1: client.AppsV1Api):
        try:
            body = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    labels=deploy_config.labels,
                    annotations=deploy_config.annotations,
                ),
                spec=client.V1DeploymentSpec(
                    replicas=deploy_config.replicas,
                    selector=client.V1LabelSelector(match_labels=deploy_config.labels),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels=deploy_config.labels,
                            annotations=deploy_config.annotations,
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=deploy_config.name,
                                    image=deploy_config.image,
                                    env=[
                                        client.V1EnvVar(name=key, value=str(value))
                                        for key, value in deploy_config.env.items()
                                    ],
                                    ports=[
                                        client.V1ContainerPort(
                                            container_port=deploy_config.port
                                        )
                                    ],
                                    resources=client.V1ResourceRequirements(
                                        limits=deploy_config.resources,
                                        requests=deploy_config.resources,
                                    ),
                                )
                            ],
                            node_selector=deploy_config.node_selector,
                            affinity=deploy_config.affinity,
                            tolerations=deploy_config.tolerations,
                            service_account=deploy_config.service_account,
                        ),
                    ),
                ),
            )
            return apps_v1.create_namespaced_deployment(
                namespace=deploy_config.namespace,
                body=body,
            )
        except client.exceptions.ApiException as e:
            if e.status == 409:
                return apps_v1.replace_namespaced_deployment(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    body=body,
                )
            else:
                raise e

    def create_service(self, deploy_config: DeployConfig, core_v1: client.CoreV1Api):
        try:
            body = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    labels=deploy_config.labels,
                    annotations=deploy_config.annotations,
                ),
                spec=client.V1ServiceSpec(
                    selector=deploy_config.labels,
                    ports=[
                        client.V1ServicePort(
                            port=deploy_config.port,
                            target_port=deploy_config.port,
                        )
                    ],
                ),
            )
            return core_v1.create_namespaced_service(
                namespace=deploy_config.namespace,
                body=body,
            )
        except client.exceptions.ApiException as e:
            if e.status == 409:
                return core_v1.replace_namespaced_service(
                    name=deploy_config.name,
                    namespace=deploy_config.namespace,
                    body=body,
                )
            else:
                raise e

    def delete_deployment(self, name: str, namespace: str, apps_v1: client.AppsV1Api):
        return apps_v1.delete_namespaced_deployment(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground",
                grace_period_seconds=5,
            ),
        )

    def delete_service(self, name: str, namespace: str, core_v1: client.CoreV1Api):
        return core_v1.delete_namespaced_service(
            name=name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy="Foreground",
                grace_period_seconds=5,
            ),
        )

    def get_deployment(self, name: str, namespace: str, apps_v1: client.AppsV1Api):
        return apps_v1.read_namespaced_deployment(
            name=name,
            namespace=namespace,
        )

    def get_service(self, name: str, namespace: str, core_v1: client.CoreV1Api):
        return core_v1.read_namespaced_service(
            name=name,
            namespace=namespace,
        )

    def update_deployment(self, deploy_config: DeployConfig, apps_v1: client.AppsV1Api):
        body = client.V1Deployment(
            metadata=client.V1ObjectMeta(
                name=deploy_config.name,
                namespace=deploy_config.namespace,
                labels=deploy_config.labels,
                annotations=deploy_config.annotations,
            ),
            spec=client.V1DeploymentSpec(
                replicas=deploy_config.replicas,
                selector=client.V1LabelSelector(match_labels=deploy_config.labels),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels=deploy_config.labels,
                        annotations=deploy_config.annotations,
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=deploy_config.name,
                                image=deploy_config.image,
                                env=[
                                    client.V1EnvVar(name=key, value=str(value))
                                    for key, value in deploy_config.env.items()
                                ],
                                ports=[
                                    client.V1ContainerPort(
                                        container_port=deploy_config.port
                                    )
                                ],
                                resources=client.V1ResourceRequirements(
                                    limits=deploy_config.resources,
                                    requests=deploy_config.resources,
                                ),
                            )
                        ],
                        node_selector=deploy_config.node_selector,
                        affinity=deploy_config.affinity,
                        tolerations=deploy_config.tolerations,
                        service_account=deploy_config.service_account,
                    ),
                ),
            ),
        )
        return apps_v1.replace_namespaced_deployment(
            name=deploy_config.name,
            namespace=deploy_config.namespace,
            body=body,
        )
