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
from constants import UNWANTED_ANNOTATIONS

kubernetes_controller = KubernetesController()
api = kubernetes_controller.get_api()


@kopf.on.login()
def custom_login_fn(**kwargs):
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
    deploy_config = DeployConfig(**spec, namespace=kwargs['body']['metadata']['namespace'])
    deployment = kubernetes_controller.create_deployment(deploy_config, name=kwargs['body']['metadata']['name'])
    service = kubernetes_controller.create_service(ServiceConfig(**deploy_config.model_dump()))
    virtual_service = kubernetes_controller.create_virtual_service(VirtualServiceConfig(**deploy_config.model_dump()))
    kopf.adopt(deployment)
    kopf.adopt(virtual_service)
    kopf.adopt(service)
    pykube.Service(api, service).create()
    pykube.Deployment(api, deployment).create()
    VirtualServiceResource(api, virtual_service).create()
    api.session.close()

    return {
        "children": [
            deployment["metadata"],
            service["metadata"],
            virtual_service["metadata"],
        ],
    }


@kopf.on.update('imran.dev.io', 'v1alpha1', 'microservices')
def update_fn(spec, **kwargs):
    """
    The update_fn function is called when a user updates an existing resource.
    The function takes the following arguments:
        spec: The specification of the resource to be updated, as defined in your CRD's schema.
        **kwargs: A dictionary containing metadata about the request and other information.  This includes things like which namespace this update was requested for, who made the request, etc...  For more details see https://github.com/kubernetes-sigs/controller-runtime/blob/master/pkg/handler/_helpers_test.go#L31
    
    :param spec: Get the configuration of the deployment
    :param **kwargs: Pass the body of the request to update_fn
    :return: A dictionary with the keys "children" and "status" containing the metadata of the updated resources and the status of the resource respectively
    :doc-author: Trelent
    """
    deploy_config = DeployConfig(
        **spec, namespace=kwargs["body"]["metadata"]["namespace"]
    )
    deployment = kubernetes_controller.update_deployment(deploy_config)
    service = kubernetes_controller.update_service(
        ServiceConfig(**deploy_config.model_dump())
    )
    virtual_service = kubernetes_controller.update_virtual_service(
        VirtualServiceConfig(**deploy_config.model_dump())
    )
    api.session.close()
    return {
        "children": [
            deployment.obj["metadata"],
            service.obj["metadata"],
            virtual_service.obj["metadata"],
        ]
    }
