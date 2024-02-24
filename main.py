import kopf
import pykube
import preflight
from custom_resources import VirtualServiceResource
from handlers.controller import KubernetesController
from schemas import (
    DeployConfig,
    ServiceConfig,
    VirtualServiceConfig,
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


@kopf.on.startup()
def prepare_fn(**_):
    """
    The prepare_fn function is called when the operator starts up.
    It is used to prepare the environment for the operator to run in.

    :param **_: Pass a variable number of keyword arguments to the function
    :return: None
    """
    preflight.run()


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
    deployment["metadata"]["name"] = service["metadata"]["name"] = kwargs["body"][
        "metadata"
    ]["name"]
    pykube.Deployment(api, deployment).create()
    pykube.Service(api, service).create()

    api.session.close()

    return {
        "children": [
            deployment["metadata"],
            service["metadata"],
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
    api.session.close()
    return {
        "children": children,
    }


kopf.on.create("imran.dev.io", "v1alpha2", "microservices")


def create_fn_v1alpha2(spec, **kwargs):
    deploy_config = DeployConfig(
        **spec, namespace=kwargs["body"]["metadata"]["namespace"]
    )
    deployment = kubernetes_controller.create_deployment(
        deploy_config, name=kwargs["body"]["metadata"]["name"]
    )
    service = kubernetes_controller.create_service(
        ServiceConfig(**deploy_config.model_dump())
    )
    virtual_service = VirtualServiceResource(
        VirtualServiceConfig(**spec, namespace=kwargs["body"]["metadata"]["namespace"])
    )
    kubernetes_controller.create_virtual_service(virtual_service)
    kopf.adopt(deployment)
    kopf.adopt(service)
    kopf.adopt(virtual_service)
    deployment["metadata"]["name"] = service["metadata"]["name"] = virtual_service[
        "metadata"
    ]["name"] = kwargs["body"]["metadata"]["name"]
    pykube.Deployment(api, deployment).create()
    pykube.Service(api, service).create()
    virtual_service.create()
    api.session.close()
    return {
        "children": [
            deployment["metadata"],
            service["metadata"],
            virtual_service.obj["metadata"],
        ],
    }


kopf.on.update("imran.dev.io", "v1alpha2", "microservices")


def update_fn_v1alpha2(spec, **kwargs):
    deploy_config = DeployConfig(
        **spec, namespace=kwargs["body"]["metadata"]["namespace"]
    )
    deployment = kubernetes_controller.update_deployment(deploy_config)
    service = kubernetes_controller.update_service(
        ServiceConfig(**deploy_config.model_dump())
    )
    virtual_service = kubernetes_controller.update_virtual_service(
        VirtualServiceConfig(**spec, namespace=kwargs["body"]["metadata"]["namespace"])
    )
    children = [
        deployment.obj["metadata"],
        service.obj["metadata"],
        virtual_service.obj["metadata"],
    ]
    api.session.close()
    return {
        "children": children,
    }
