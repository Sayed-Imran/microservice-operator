# Microservice Operator

This operator is a Kubernetes operator that manages microservices. It is built using the [kopf](https://github.com/nolar/kopf) framework, which is a Python framework for Kubernetes operators.

Any microservice API which is developed, needs to be deployed and exposed as a Kubernetes service and all sits behind a proxy. This operator automates the process of deploying as Kubernetes Deployment and exposing the same as a Kubernetes service and also putting the same behind a proxy using Istio's VirtualService and Gateway.

## Contents

0. [Prerequisites](#prerequisites)
1. [Operator Installation](#installation)
2. [Usage](#usage)
3. [Development](#development)


## Prerequisites

As the operator uses Istio's VirtualService and Gateway, the Istio service mesh needs to be installed in the Kubernetes cluster. Refer to the [Istio documentation](https://istio.io/latest/docs/setup/getting-started/#download) for installation instructions.

## Operator Installation

Clone the repository and change directory to the repository:

```bash
git clone https://github.com/Sayed-Imran/microservice-operator.git
cd microservice-operator
```

Single command to install the operator:

```bash
kubectl apply -k manifests/install/
```

## Usage

The operator can be used by creating a custom resource of kind `Microservice`. The following is an example of a custom resource:

```yaml
apiVersion: imran.dev.io/v1alpha1
kind: Microservice
metadata:
  name: micron
spec:
  labels:
    app: microservice-sample
    env: dev
  replicas: 3
  image: sayedimran/fastapi-sample-app:v4
  port: 7000
  path: /api/v1
  env:
    - name: ENV
      value: dev
    - name: LOG_LEVEL
      value: debug
  resources:
    limits:
      cpu: 100m
      memory: 128Mi
    requests:
      cpu: 100m
      memory: 128Mi
```

The above custom resource will create a deployment with 3 replicas and expose the same as a service. The deployment will use the image `sayedimran/fastapi-sample-app:v4`, will create a Kubernetes Service to expose the deployment over port 7000, and will put microservice behind proxy `/api/v1/`. The environment variables `ENV` and `LOG_LEVEL` will be set to `dev` and `debug` respectively. The resources for the deployment will be limited to 100m CPU and 128Mi memory and the requests will be the same.

## Development

To start developing the operator, the following steps can be followed:

1. Clone the repository:

```bash
git clone https://github.com/Sayed-Imran/microservice-operator.git
```

2. Change directory to the repository:

```bash
cd microservice-operator
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the operator:

```bash
kopf run main.py --verbose
```
