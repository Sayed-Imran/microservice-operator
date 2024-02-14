import kopf
import pykube
from handlers.py_kube_controller import KubernetesController
from schemas import (
    DeployConfig,
    ServiceConfig,
    VirtualServiceConfig,
    VirtualServiceResource,
)
from config import EnvConfig

kubernetes_controller = KubernetesController()
api = kubernetes_controller.get_api()


@kopf.on.login()
def custom_login_fn(**kwargs):
    """
    The custom_login_fn function is used to determine how the operator will authenticate with the Kubernetes API.
    If we are running in a development environment, then we want to use our local kubeconfig file.
    Otherwise, if we are running in a production environment (i.e., on OpenShift), then we want to use the service account token.

    :param **kwargs: Pass a variable number of keyword arguments to the function
    :return: A function
    """
    if EnvConfig.ENV == "dev":
        return kopf.login_with_kubeconfig(**kwargs)
    else:
        return kopf.login_with_service_account(**kwargs)


@kopf.on.create("imran.dev.io", "v1alpha1", "microservices")
def create_fn(spec, **kwargs):
    """
    The create_fn function is called when a new instance of the CustomResource is created.
    It creates a deployment, service and virtualservice in the same namespace as the CustomResource.
    The deployment has one replica by default, but this can be changed by setting replicas in spec.
    
    :param spec: Create a deployconfig object
    :param **kwargs: Pass the namespace and name of the resource to be created
    :return: A dictionary containing the metadata of the created resources
    :doc-author: Trelent
    """
    deploy_config = DeployConfig(
        **spec, namespace=kwargs["body"]["metadata"]["namespace"]
    )
    deployment = kubernetes_controller.create_deployment(
        deploy_config, name=kwargs["body"]["metadata"]["name"]
    )
    service = kubernetes_controller.create_service(
        ServiceConfig(**deploy_config.model_dump())
    )
    kopf.adopt(deployment)
    kopf.adopt(service)
    pykube.Deployment(api, deployment).create()
    pykube.Service(api, service).create()
    if spec.get("path"):
        virtual_service = kubernetes_controller.create_virtual_service(
            VirtualServiceConfig(**deploy_config.model_dump())
        )
        kopf.adopt(virtual_service)
        VirtualServiceResource(api, virtual_service).create()
    api.session.close()

    return {
        "children": [
            deployment["metadata"],
            service["metadata"],
            virtual_service["metadata"],
        ],
    }


@kopf.on.update("imran.dev.io", "v1alpha1", "microservices")
def update_fn(spec, **kwargs):
    """
    The update_fn function is called when a user updates an existing resource.
    The function takes the following arguments:
        spec: The specification of the resource to be updated, as defined in your CRD's schema.
        **kwargs: A dictionary containing metadata about the request and other information.  This includes things like which namespace this update was requested for, who made the request, etc.

    :param spec: Get the configuration of the deployment
    :param **kwargs: Pass the body of the request to update_fn
    :return: A dictionary with the keys "children" and "status" containing the metadata of the updated resources and the status of the resource respectively
    """
    deploy_config = DeployConfig(
        **spec, namespace=kwargs["body"]["metadata"]["namespace"]
    )
    deployment = kubernetes_controller.update_deployment(deploy_config)
    service = kubernetes_controller.update_service(
        ServiceConfig(**deploy_config.model_dump())
    )
    children = [deployment.obj["metadata"], service.obj["metadata"]]
    if spec.get("path"):
        virtual_service = kubernetes_controller.update_virtual_service(
            VirtualServiceConfig(**deploy_config.model_dump())
        )
        children.append(virtual_service.obj["metadata"])
    api.session.close()
    return {
        "children": children,
    }
