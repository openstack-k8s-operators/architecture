# Configuring networking and deploy the OpenStack control plane

## Assumptions

- A storage class called `lvms-local-storage` should already exist.

## Initialize

Switch to the "openstack" namespace

```shell
oc project openstack
```

Change to the dcn directory

```shell
cd architecture/examples/dt/dcn
```

Edit the [control-plane/nncp/values.yaml](control-plane/nncp/values.yaml) file to suit your environment.

```shell
vi control-plane/nncp/values.yaml
```

## Apply node network configuration

Generate the node network configuration

```shell
kustomize build control-plane/nncp > nncp.yaml
```

Apply the NNCP CRs

```shell
oc apply -f nncp.yaml
```

Wait for NNCPs to be available

```shell
oc wait nncp -l osp/nncm-config-type=standard --for jsonpath='{.status.conditions[0].reason}'=SuccessfullyConfigured --timeout=300s
```

## Apply networking and control-plane configuration

Generate the control-plane and networking CRs.

```shell
kustomize build control-plane > control-plane.yaml
```

Apply the CRs

```shell
oc apply -f control-plane.yaml
```

Wait for control plane to be available

```shell
oc wait osctlplane controlplane --for condition=Ready --timeout=600s
```
