# Microservice Operator

This operator is a Kubernetes operator that manages microservices. It is built using the [kopf](https://github.com/nolar/kopf) framework, which is a Python framework for Kubernetes operators.

Any microservice API which is developed, needs to be deployed and exposed as a Kubernetes service. This operator automates the process of deploying as Kubernetes Deployment and exposing the same as a Kubernetes service.

## Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Development](#development)


## Installation

For the operator to be installed, the crd needs to be installed first. The crd can be installed using the following command:

```bash
 kubectl apply -f https://raw.githubusercontent.com/Sayed-Imran/microservice-operator/main/crd.yml
```

To install the operator, the following command can be used:

```bash
 kubectl apply -f https://raw.githubusercontent.com/Sayed-Imran/microservice-operator/main/deploy.yml
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

The above custom resource will create a deployment with 3 replicas and expose the same as a service. The deployment will use the image `sayedimran/fastapi-sample-app:v4` and will expose the service on port `7000`. The environment variables `ENV` and `LOG_LEVEL` will be set to `dev` and `debug` respectively. The resources for the deployment will be limited to 100m CPU and 128Mi memory.

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
