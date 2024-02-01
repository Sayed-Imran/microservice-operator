import kopf
import pykube
from handlers.py_kube_controller import KubernetesController
from schemas import DeployConfig


kubernetes_controller = KubernetesController()
api = kubernetes_controller.get_api()

@kopf.on.create('imran.dev.io', 'v1alpha1', 'microservices')
def create_fn(spec, **kwargs):
    deploy_config = DeployConfig(**spec)
    deployment = kubernetes_controller.create_deployment(deploy_config)
    kopf.adopt(deployment)
    pykube.Deployment(api, deployment).create()
    service = kubernetes_controller.create_service(deploy_config)
    kopf.adopt(service)
    pykube.Service(api, service).create()
    api.session.close()
    return {"children": [deployment.metadata['uid'], service.metadata['uid']]}


# @kopf.on.delete('imran.dev.io', 'v1alpha1', 'microservices')
# def delete_fn(spec, **kwargs):
