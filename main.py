import kopf
import pykube
from handlers.py_kube_controller import KubernetesController
from schemas import DeployConfig, ServiceConfig, VirtualServiceConfig, VirtualServiceResource
from config import EnvConfig

kubernetes_controller = KubernetesController()
api = kubernetes_controller.get_api()

@kopf.on.login()
def custom_login_fn(**kwargs):
    if EnvConfig.ENV == 'dev':
        return kopf.login_with_kubeconfig(**kwargs)
    else:
        return kopf.login_with_service_account(**kwargs)



@kopf.on.create('imran.dev.io', 'v1alpha1', 'microservices')
def create_fn(spec, **kwargs):
    deploy_config = DeployConfig(**spec, namespace=kwargs['body']['metadata']['namespace'])
    deployment = kubernetes_controller.create_deployment(deploy_config, name=kwargs['body']['metadata']['name'])
    kopf.adopt(deployment)
    pykube.Deployment(api, deployment).create()
    service = kubernetes_controller.create_service(ServiceConfig(**deploy_config.model_dump()))
    kopf.adopt(service)
    pykube.Service(api, service).create()
    virtual_service = kubernetes_controller.create_virtual_service(VirtualServiceConfig(**deploy_config.model_dump()))
    kopf.adopt(virtual_service)
    VirtualServiceResource(api, virtual_service).create()
    api.session.close()

    return {"children": [deployment["metadata"], service['metadata'], virtual_service['metadata']], }


@kopf.on.update('imran.dev.io', 'v1alpha1', 'microservices')
def update_fn(spec, **kwargs):
    deploy_config = DeployConfig(**spec, namespace=kwargs['body']['metadata']['namespace'])
    deployment = kubernetes_controller.update_deployment(deploy_config)
    service = kubernetes_controller.update_service(ServiceConfig(**deploy_config.model_dump()))
    virtual_service = kubernetes_controller.update_virtual_service(VirtualServiceConfig(**deploy_config.model_dump()))
    api.session.close()
    return {"children": [deployment.obj['metadata'], service.obj['metadata'], virtual_service.obj['metadata']] }
